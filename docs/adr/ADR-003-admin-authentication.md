# ADR-003: Admin Authentication with Argon2 and Server-Side Sessions

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

The admin dashboard must be protected: only the shop owner may manage
products and orders. This requires authentication (proving identity) and a
way to persist login across requests. Two sub-decisions: how to hash
passwords, and how to manage login sessions.

## Decision

**Password hashing: Argon2id** (via `argon2-cffi`), using the library's
default parameters.

**Session management: server-side sessions.** An opaque token is stored in an
`HttpOnly` cookie; session data (which admin, expiry) lives in an
`admin_sessions` table.

## Alternatives considered

- **bcrypt** for hashing — still secure, but Argon2id is the current OWASP
  recommendation for new applications: memory-hard (resists GPU/ASIC attacks)
  and free of bcrypt's 72-byte input truncation. Since this is a new project
  with no legacy hashes, Argon2id is chosen outright.
- **Signed cookies (JWT-style)** for sessions — self-contained and stateless,
  but cannot be revoked before expiry without extra infrastructure.
  Server-side sessions can be revoked instantly (delete the row), which
  matters for admin access.

## Consequences

**Positive**
- Passwords are never stored or recoverable; a breach yields useless hashes.
- Sessions are instantly revocable (logout genuinely destroys them).
- Failed logins give an identical response for bad email vs bad password,
  preventing account enumeration.

**Negative / accepted trade-offs**
- Argon2 uses meaningful memory per hash (~tens of MiB). Irrelevant for admin
  login volume; would warrant parameter review if used for high-volume
  customer logins on a small server.
- Server-side sessions require a database lookup per protected request and a
  periodic cleanup of expired session rows (to be added).

## Revisit if

Customer accounts are added at scale (revisit Argon2 parameters and possibly
session strategy), or if a stateless/multi-server deployment makes signed
tokens more practical.
