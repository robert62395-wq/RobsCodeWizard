## v0.4.6.1 - 2026-06-22 - Hotfix: validator/suggester suffix-strip logic

### Fixed
- `app/services/validator.py` and `app/services/suggester.py`:
  Both modules now check the full token against valid_set BEFORE falling
  back to the stripped-suffix form. Previously, codes like PI1 (where
  the trailing digit is part of the canonical code, not a string ID)
  were incorrectly stripped to PI and reported as unknown.
- Same fix applied to the size-bearing lookahead so size tokens are
  correctly recognized.
- Phase 6 tests now all 36 pass.
