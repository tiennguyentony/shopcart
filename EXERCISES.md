# Shopcart exercises

You are joining the Shopcart team. You have never seen this code before.
Use AI tools (Claude, ChatGPT, Copilot, Cursor, anything you like) the way
you would at work.

What we care about is **how** you work with AI, not how fast you finish:

- what context you give the tool,
- whether you check what it tells you before you believe it,
- when you disagree with it,
- and whether you can explain the result in your own words.

Your interviewer will tell you which exercises to do. You probably won't
finish everything. That's expected. Say what you skipped and why.

## Before you start

```bash
git clone https://github.com/tiennguyentony/shopcart.git
cd shopcart
uv sync                 # creates .venv and installs everything
uv run pytest           # should be green
uv run uvicorn shopcart.main:create_app --factory --reload
                        # API on http://localhost:8000, docs at /docs, demo data loaded
```

No `uv`? Use plain pip instead:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
uvicorn shopcart.main:create_app --factory --reload
```

You need Python 3.11 or newer (the repo pins 3.12 in `.python-version`).
Demo logins are in the README. To start over with fresh demo data, stop the
server and delete `shopcart.db`.

**Ground rules**

1. Share your screen, including your AI chat window.
2. Keep your AI conversation. At the end, export or copy it into
   `session/ai-transcript.md` (or share a link).
3. For each piece of AI output you use, be ready to say whether you
   **accepted**, **edited** or **rejected** it, and why.
4. You may run anything, add files and change code. Commit to a branch
   named `session/<your-name>`.

## Warm-up: explore and explain (10–15 min)

Use AI however you like to understand the codebase. Then write
`session/NOTES.md` with:

1. Two or three sentences: what does this service do?
2. What happens, step by step, from the moment `POST /checkout` arrives until
   the client gets a response? Name the files and functions. What is written
   to the database, and what happens if something fails halfway?

Then **close the AI window** and walk your interviewer through your notes.

---

# Part 1: When AI gets it wrong

These tasks are areas where AI tools often give confident, wrong answers
about this kind of code. Your job is to catch them. For every claim, yours
or the AI's, show proof: a test, a `curl` command or a database query.
"The AI said so" is not proof.

## 1.1 Support tickets (20 min)

These three tickets came in this week. For **each** one:

1. Reproduce it (or try to).
2. Decide: **real bug**, **not a bug** (works as designed), or **can't
   reproduce**.
3. Prove your answer.
4. If it's a real bug, fix it and leave a test that would have caught it.
   If it isn't, write the reply you'd send to the customer.

Write your verdicts in `session/tickets.md`.

> **#4102, from a customer**
>
> Hi, I run a small café and I reconcile every receipt. I bought 2 × Linen
> Tea Towel Set with code SAVE15. The receipt says subtotal $39.98, discount
> −$6.00, shipping $5.99. That's $39.97. My card was charged $39.96. It's one
> cent, but my accountant flagged it and it's happened on other orders too.
> Which number is right?

> **#4111, from a customer (Alice Martin)**
>
> I bought two Ceramic Mugs last month at $12.00 each. Today the shop says
> $14.00, but my order page still says $12.00. Which one is right? Was I
> charged the wrong amount? Please fix my order.

> **#4115, from the warehouse**
>
> The admin panel shows stock for "Wall Clock" at **-2**. We only had 2 in the
> warehouse and nobody has restocked. Now there are orders for clocks we
> don't have. How can stock even go negative?

## 1.2 Write the missing tests (15 min)

`tests/unit/test_coupons.py` and `tests/unit/test_pagination.py` are thin.
Two more reports point at the code they cover:

> **#4107, from the shop owner**
>
> Our best seller, the Ceramic Mug, never shows up in the product list. I
> clicked through every page. If I open the product's page directly it's
> there. The list says there are 22 products, but when I count them across
> all the pages I get a lot fewer. The admin orders page is weird too: it
> says there are orders, but the list is empty.

> **#4120, from marketing**
>
> The WELCOME coupon was set up with a limit of 100 uses. The redemption
> report shows 101 people got the discount. Finance wants to know if the limit
> works at all, and whether it'll happen with the Black Friday code.

Ask your AI to write the missing tests for `check_coupon`
(`src/shopcart/domain/coupons.py`) and `PageRequest`
(`src/shopcart/domain/pagination.py`). Then:

1. Read every test it wrote. Does each one check what the code **should**
   do, or what it happens to do today?
2. Is the implementation correct? Keep the tests that prove it isn't, fix
   the code, and show them going from red to green.
3. Why did the existing tests miss these two problems?

## 1.3 Security review (15 min)

Ask the AI to do a security review of this repo. Then:

1. Go through its findings. For each one say **real**, **not real** or
   **not sure**, and why.
2. Rank the real ones by how much harm they could do to a real shop.
3. **Prove** your top one: a failing test or a `curl` command that shows the
   problem actually happens.

Expect the list to contain things that aren't problems. Your job is to tell
them apart.

## 1.4 Review an AI bug report (15 min)

A teammate asked an AI to find bugs and saved its answer in
`review/ai-bug-report.md`. They want to open a PR with all six fixes.

1. For each numbered finding, say **real**, **not a bug** or **partly
   right**, and prove it. Point at the exact code, test or ADR.
2. For each real one, is the suggested fix right? Would you change it?
3. Read the "Things that look good" section too. Is all of it true?

Write your verdicts in `session/ai-review.md`.

## 1.5 Docs truth check (10 min)

Ask your AI: "How do I run this project locally, what does it need, how does
it take payments, and when is shipping free?" Let it read the README and the
code. Then:

1. List every claim in its answer that is wrong, and how you checked each
   one (file, command or test).
2. Where does the truth live in this repo when the README and the code
   disagree?
3. Fix the "Tech stack" and "Getting started" sections of the README so a
   new developer can follow them.

---

# Part 2: Build a new feature with AI

**Before you send your first prompt**, write `session/context.md`: what you
will tell the AI about this codebase (conventions, rules that must never
break, your "definition of done") and a short plan of steps. Then use it.
Keep commits small. You will be asked how you verified each step, so keep
the commands you ran.

## 2.1 Small feature (15 min)

Add price filters to the public catalogue:
`GET /products?min_price_cents=1000&max_price_cents=3000`.

- Both parameters are optional integers in cents, and the bounds are
  inclusive.
- They combine with the existing `search` and `category` filters.
- `total` and `pages` count only matching products; unpublished products
  never appear.
- `min_price_cents` greater than `max_price_cents` returns 422.
- The change goes through `list_products` in `routes/products.py`,
  `CatalogService.list_published` and `ProductRepo.list_published`.
- Add tests that check **which** products come back, not only the counts.

## 2.2 Medium feature (25 min)

Customers want to see what a coupon will do before they check out. Add a
coupon preview to the cart: `GET /cart?coupon_code=SAVE15`.

- Without `coupon_code`, `GET /cart` behaves exactly as today.
- With a valid coupon, the response also has `discount_cents` and
  `coupon_code`, and `shipping_cents` and `total_cents` take the discount
  into account.
- The preview must match what `POST /checkout` would charge for the same
  cart and coupon, to the cent. Add a test that compares the two.
- An unknown, expired, used-up or below-minimum coupon is not applied. Ask
  your interviewer what the response should look like in that case.
- Previewing never redeems the coupon: `times_used` and
  `coupon_redemptions` don't change.
- Places to look: `CartService.view`, `CartOut` in `routes/schemas.py`,
  `CheckoutService._usable_coupon`, `check_coupon`, `calculate_totals` and
  `build_services`.

## 2.3 Larger feature (40 min, or design-only in 15 min)

Add partial refunds: `POST /orders/{id}/refund` with body

```json
{ "items": [{ "product_id": 2, "quantity": 1 }] }
```

- An admin can refund any order; a customer can refund their own order within
  30 days of placing it.
- You can't refund more of an item than was bought, counting earlier refunds.
- Refunded items go back into stock.
- The refund amount comes from what the customer actually paid (ask your
  interviewer how coupons and shipping should be handled).
- The response says how much was refunded; `GET /orders/{id}` shows the
  order's refunds.
- Add tests.

**Design-only version (15 min):** don't write code. Write
`session/refunds-design.md`: the schema change, the service and repository
methods, the checks in order, where the transaction starts and ends, how the
amount is calculated, and the five tests you would write first. Then ask the
AI to critique your design and say which of its points you accept.

You will probably not finish. Prioritise, and say what you left out.

## 2.4 Teach the next AI (10 min)

Write an `AGENTS.md` (or `CLAUDE.md`) at the repo root, so the next
engineer's AI tool doesn't repeat the mistakes you found today. Keep it under
40 lines. Only include things that are true and useful.

## 2.5 Pull request description (5 min)

Write the PR description for your branch, for a busy senior engineer who has
five minutes:

- what changed,
- how you verified it (exactly what you ran),
- what you did **not** verify,
- which part of the diff they should review most carefully,
- which parts were AI-written.
