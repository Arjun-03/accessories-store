# ADR-001: Use PayHere as the Payment Gateway

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

The store operates in Sri Lanka and needs to accept online card payments
(planned as an early post-launch feature).

The original brief assumed Stripe or PayPal. On investigation:
- **Stripe** does not support businesses based in Sri Lanka; using it would
  require incorporating a company abroad — not viable for this business.
- **PayPal** has significant limitations for receiving/withdrawing funds in
  Sri Lanka.
- **PayHere** is the most widely used gateway among Sri Lankan e-commerce
  sites, supports LKR and local wallets, and offers documented APIs and a
  sandbox.

The MVP launches with Cash on Delivery + bank transfer, so no gateway is
needed at launch — but the architecture must not lock us out of adding one.

## Decision

Use **PayHere** as the payment gateway, integrated behind a provider-agnostic
payment interface so a second provider can be added later without a rewrite.

## Consequences

**Positive**
- Works for a Sri Lanka-based business, unlike Stripe/PayPal.
- Local payment methods increase customer trust and conversion.
- The modular interface keeps us from being locked to one provider.

**Negative / Risks**
- Less familiar than Stripe; smaller community and fewer examples.
  *Mitigation:* spike PayHere's sandbox before committing to the integration.
- PayHere's callback model requires a public URL for webhooks, which
  complicates local development. *To be addressed when we build payments.*

## Revisit if

Stripe or another major provider begins supporting Sri Lankan businesses, or
if PayHere's fees/reliability prove problematic in production.