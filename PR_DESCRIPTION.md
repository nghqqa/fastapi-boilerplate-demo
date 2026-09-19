# PR (demo): enforce unique API-key names per user

## Background
Business rule: one user must not hold two API keys with the same name.
Adds composite UNIQUE(user_id, name) on api_keys (model + migration in lockstep).

## Expected behaviour
- Empty databases: constraint applies on upgrade.
- Historical databases: duplicates (legal until now) are deduplicated
  (keep one name owner, suffix the others) BEFORE the constraint is created.

## Known risk (SEEDED)
The migration as committed (revision demo0001) creates the constraint
WITHOUT dedupe. Any environment where a user already has same-named keys
fails upgrade with an IntegrityError - deterministic reproducer:
backend/tests/integration/migrations/test_uq_user_key_name.py::
test_historical_duplicates_upgrade_fails  (this test FAILS by design
until the fix lands).

## Acceptance criteria (Verifier)
1. Empty-DB upgrade succeeds; constraint present in inspector.
2. Historical-DB (duplicate rows) upgrade SUCCEEDS after the fix;
   post-conditions asserted: rows still 2, names now unique, key hashes
   unchanged.
3. Re-running upgrade is idempotent; downgrade drops the constraint.
4. Existing API response schemas unchanged (additive only).
5. Full backend suite green: 162 baseline unit tests + both migration
   tests above.

## Unacceptable fixes
- Deleting historical duplicate keys to force a pass.
- Weakening the constraint (partial/filtered) without product sign-off.
- Skipping the migration and relying on CREATE_TABLES_ON_STARTUP.
