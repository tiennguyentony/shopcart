import hashlib
import hmac
import secrets
import sqlite3
from datetime import timedelta

from shopcart.clock import Clock, to_iso
from shopcart.domain.errors import Unauthorized
from shopcart.repositories.users import User, UserRepo


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, conn: sqlite3.Connection, users: UserRepo, clock: Clock, session_ttl_hours: int):
        self.conn = conn
        self.users = users
        self.clock = clock
        self.session_ttl = timedelta(hours=session_ttl_hours)

    def login(self, email: str, password: str) -> str:
        user = self.users.by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise Unauthorized("Invalid email or password")

        token = secrets.token_urlsafe(32)
        expires_at = to_iso(self.clock.now() + self.session_ttl)
        with self.conn:
            self.users.create_session(hash_token(token), user.id, expires_at)
        return token

    def user_for_token(self, token: str) -> User | None:
        return self.users.by_session(hash_token(token), to_iso(self.clock.now()))
