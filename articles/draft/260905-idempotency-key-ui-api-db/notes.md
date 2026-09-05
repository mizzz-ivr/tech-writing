# Idempotency article verification notes

## Public article boundary

The Zenn canonical article must not expose project names, repository names, internal URLs, private resource IDs, production-specific identifiers, secrets, or environment-specific values.

The public article uses generic examples such as `POST /notices`, `resource=R1`, and `key=A`.

## Verified implementation facts (2026-09-05)

- UI keeps pending mutation keys in memory together with an operation fingerprint.
- Matching fingerprint reuses the existing key.
- Successful mutation clears the key.
- A response classified as definitive clears the key; ambiguous network/server failure keeps it available for retry.
- Browser validates static schedule constraints but does not reject a schedule solely because the end time is already in the past before the canonical replay boundary.
- API validates the idempotency key and ordinary mutation security/validation boundaries.
- Database serializes same-request keys with transaction-level PostgreSQL advisory locks.
- Exact replay/conflict resolution occurs before time-dependent eligibility for create.
- Fresh wall-clock time is read after lock/replay resolution before time-dependent eligibility.
- Reuse of one request ID for a different target/action converges to conflict.

## External references checked

- RFC 9110 §9.2.2 Idempotent Methods.
- PostgreSQL advisory lock documentation.
- PostgreSQL date/time functions: `now()` / `transaction_timestamp()` vs `clock_timestamp()`.

## Publication check

- Re-fetch the implementation source before publication.
- Do not claim production behavior unless production acceptance has been independently confirmed.
- Keep `published: false` until final preview and publication decision.
