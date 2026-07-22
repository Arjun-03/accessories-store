# Vision & MVP Scope

## Vision

An online store where customers in Sri Lanka can easily discover and buy
handmade press-on nails, with a shopping experience that feels trustworthy
and personal — built on a foundation that can grow into a full accessories
brand without being rebuilt.

## Target market

Sri Lanka only (currency: LKR).

## MVP scope

The smallest version that lets a real customer place a real order.

### In the MVP (build now)
- Product catalogue: list + detail pages (name, description, price, images, stock, SKU)
- Cart and guest checkout (no accounts required)
- Payment: Cash on Delivery + bank transfer
- Orders saved to database; owner can view and update order status
- Minimal secure admin: add/edit products, manage orders
- Landing page and Contact page

### Deferred (later milestones)
- Customer accounts: registration, login, password reset, email verification, saved addresses
- PayHere online card payments (early post-launch milestone)
- Search, filtering, tags, featured products, new arrivals
- Coupons, shipping calculator, tax logic
- Order history, tracking, invoice downloads
- Reviews, wishlist, analytics dashboard
- About and FAQ pages

## Key decisions
- **Guest checkout at launch** — a new customer wants to buy, not register.
- **COD + bank transfer at launch** — builds trust for an unknown brand; card payments (PayHere) come as an early upgrade.
- **One category now, multi-category data model** — we sell only press-on nails
  at launch, but the database is designed so new categories (earrings, etc.)
  are added as data, not rebuilt.
