# ADR-002: Store Cart Contents in the Database, Not the Cookie

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Guest customers (no accounts at launch) need a cart that persists across
requests. HTTP is stateless, so the cart must be tied to the visitor somehow.
A cart is identified by a token the browser carries in a cookie — but the
cart's *contents* (which products, what quantities) could live in one of two
places:

- **In the cookie itself** — the whole cart encoded client-side.
- **In the database** — a `carts` / `cart_items` table, with only an opaque
  token in the cookie.

The cart contains prices, which are security-sensitive: if a customer could
alter the price, they could check out at a price they set.

## Decision

Store cart contents in the database. The cookie holds only an opaque,
cryptographically random session token that identifies which cart is whose.
Cart items store no price; prices are always read live from `products`.

## Alternatives considered

- **Signed cookie cart.** A cookie-stored cart with a cryptographic signature
  the server verifies, detecting tampering. This is secure when implemented
  correctly and avoids database writes for browsing visitors. Rejected mainly
  for reasons below, not because it is unsafe.

## Consequences

**Positive**
- Cart contents are categorically out of the client's reach — no signing to
  get exactly right, no price-tampering surface.
- Directly reusable when accounts arrive: a logged-in user's cart, saved
  addresses, and order history all build on server-side cart data.
- Enables future features (abandoned-cart analysis, cross-device carts).

**Negative / accepted trade-offs**
- Every cart mutation is a database write. Negligible at our scale.
- Anonymous carts accumulate and need periodic cleanup of stale rows
  (a scheduled job, to be added later).

## Revisit if

Database write load from carts ever becomes a measured problem, or if the
project moves to a stateless/edge architecture where a signed cookie cart
would fit better.
