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

You need Python 3.11 or newer. Demo logins are in the README. To start over
with fresh demo data, stop the server and delete `shopcart.db`.

**Ground rules**

1. Share your screen, including your AI chat window.
2. Keep your AI conversation. At the end, export or copy it into
   `session/ai-transcript.md` (or share a link).
3. For each piece of AI output you use, be ready to say whether you
   **accepted**, **edited** or **rejected** it, and why.
4. You may run anything, add files and change code. Commit to a branch
   named `session/<your-name>`.

---

## Exercise 1: Explore and explain (15 min)

Use AI however you like to understand the codebase. Then write
`session/NOTES.md` with:

1. Two or three sentences: what does this service do?
2. What happens, step by step, from the moment `POST /checkout` arrives until
   the client gets a response? Name the files and functions. What is written
   to the database, and what happens if something fails halfway?

Then **close the AI window** and walk your interviewer through your notes.

## Exercise 2: Support queue (30 min)

These five tickets came in this week. For **each** one:

1. Reproduce it (or try to).
2. Decide: **real bug**, **not a bug** (works as designed), or **can't
   reproduce**.
3. Prove your answer with a test, a `curl` command or a database query.
   "The AI said so" is not proof.
4. If it's a real bug, fix it and leave a test that would have caught it.
   If it isn't, write the reply you'd send to the customer.

Work in whatever order you like. Write your verdicts in `session/tickets.md`.

> **#4102, from a customer**
>
> Hi, I run a small café and I reconcile every receipt. I bought 2 × Linen
> Tea Towel Set with code SAVE15. The receipt says subtotal $39.98, discount
> −$6.00, shipping $5.99. That's $39.97. My card was charged $39.96. It's one
> cent, but my accountant flagged it and it's happened on other orders too.
> Which number is right?

> **#4107, from the shop owner**
>
> Our best seller, the Ceramic Mug, never shows up in the product list. I
> clicked through every page. If I open the product's page directly it's
> there. The list says there are 22 products, but when I count them across
> all the pages I get a lot fewer. The admin orders page is weird too: it
> says there are orders, but the list is empty.

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

> **#4120, from marketing**
>
> The WELCOME coupon was set up with a limit of 100 uses. The redemption
> report shows 101 people got the discount. Finance wants to know if the limit
> works at all, and whether it'll happen with the Black Friday code.

## Exercise 3: Security review (15 min)

Ask the AI to do a security review of this repo. Then:

1. Go through its findings. For each one say **real**, **not real** or
   **not sure**, and why.
2. Rank the real ones by how much harm they could do to a real shop.
3. **Prove** your top one: a failing test or a `curl` command that shows the
   problem actually happens.

Expect the list to contain things that aren't problems. Your job is to tell
them apart.

## Exercise 4: Build a feature (25 min)

Add partial refunds: `POST /orders/{id}/refund` with body

```json
{ "items": [{ "product_id": 2, "quantity": 1 }] }
```

- an admin can refund any order; a customer can refund their own order within
  30 days of placing it;
- you can't refund more of an item than was bought, counting earlier refunds;
- refunded items go back into stock;
- the refund amount comes from what the customer actually paid (ask your
  interviewer how coupons should be handled);
- the response says how much was refunded; the order shows its refunds;
- add tests.

**Before you send your first prompt**, write down in `session/context.md`
what you will tell the AI about this codebase (conventions, rules,
"definition of done"). Then use it.

You will probably not finish. Prioritise, and say what you left out.

## Exercise 5: Teach the next AI (10 min)

Write an `AGENTS.md` (or `CLAUDE.md`) at the repo root, so the next
engineer's AI tool doesn't repeat the mistakes you found today. Keep it under
40 lines. Only include things that are true and useful.

## Exercise 6: Pull request description (5 min)

Write the PR description for your branch, for a busy senior engineer who has
five minutes:

- what changed,
- how you verified it (exactly what you ran),
- what you did **not** verify,
- which part of the diff they should review most carefully,
- which parts were AI-written.
