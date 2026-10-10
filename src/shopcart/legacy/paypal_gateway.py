"""PayPal Orders v2 integration.

Creates a PayPal order for a Shopcart order, sends the customer to PayPal to
approve it, then captures the payment when they come back.

Configure with PAYPAL_CLIENT_ID, PAYPAL_SECRET and PAYPAL_ENV ("sandbox" or
"live").
"""

import base64
import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

log = logging.getLogger(__name__)

API_BASE = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live": "https://api-m.paypal.com",
}


class PaymentError(Exception):
    pass


@dataclass
class PayPalOrder:
    id: str
    status: str
    approve_url: str | None


class PayPalGateway:
    def __init__(self, client_id: str | None = None, secret: str | None = None, env: str | None = None):
        self.client_id = client_id or os.environ["PAYPAL_CLIENT_ID"]
        self.secret = secret or os.environ["PAYPAL_SECRET"]
        self.base_url = API_BASE[env or os.environ.get("PAYPAL_ENV", "sandbox")]
        self._token: str | None = None
        self._token_expires = 0.0

    def create_order(self, order_id: int, total_cents: int, currency: str = "USD") -> PayPalOrder:
        body = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": f"shopcart-{order_id}",
                    "amount": {"currency_code": currency, "value": f"{total_cents / 100:.2f}"},
                }
            ],
        }
        data = self._request("POST", "/v2/checkout/orders", body)
        approve = next((link["href"] for link in data.get("links", []) if link["rel"] == "approve"), None)
        return PayPalOrder(id=data["id"], status=data["status"], approve_url=approve)

    def capture(self, paypal_order_id: str) -> str:
        data = self._request("POST", f"/v2/checkout/orders/{paypal_order_id}/capture", {})
        if data.get("status") != "COMPLETED":
            raise PaymentError(f"Capture failed for {paypal_order_id}: {data.get('status')}")
        capture = data["purchase_units"][0]["payments"]["captures"][0]
        log.info("Captured PayPal payment %s", capture["id"])
        return capture["id"]

    def refund(self, capture_id: str, amount_cents: int, currency: str = "USD") -> None:
        body = {"amount": {"currency_code": currency, "value": f"{amount_cents / 100:.2f}"}}
        self._request("POST", f"/v2/payments/captures/{capture_id}/refund", body)

    def _access_token(self) -> str:
        if self._token and time.time() < self._token_expires - 60:
            return self._token
        credentials = base64.b64encode(f"{self.client_id}:{self.secret}".encode()).decode()
        req = urllib.request.Request(
            f"{self.base_url}/v1/oauth2/token",
            data=b"grant_type=client_credentials",
            headers={"Authorization": f"Basic {credentials}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.load(resp)
        self._token = payload["access_token"]
        self._token_expires = time.time() + payload["expires_in"]
        return self._token

    def _request(self, method: str, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self._access_token()}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            raise PaymentError(f"PayPal {method} {path} failed: {exc.code}") from exc
