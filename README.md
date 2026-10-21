# Experimental menu/offline patch mirror — v2

**Experimental: not tested in the game, not a verified full unlock.**

This repository is separate from `TanTrieuNguyen/ff_client`. It contains the
captured iOS 1.132.11 resources with one experimental patch and updated manifest.
V1 replaced four `res_key_exp` reads; the user reported its features working.
V2 preserves those changes and adds 14 instruction edits:
- Render/hit-test three equal-width tabs: ESP, AIM, MISC; clamp old KEY selection.
- Skip the KEY content block, forced key-tab selection and authentication scheduler.
- Return immediately from the four identified request/response/license-state helpers.
- Remove obsolete activation-warning text and the unactivated header fallback.
See `v2-changes.json`. Opcode mapping remains inferred. The underlying dead code,
strings and previously saved key preferences are not physically deleted.
The changed expiry value is limited by signed Unix time in January 2038.

## Test
Import `proxypin-experimental.json` into ProxyPin. Disable other rules rewriting
`abhotupdate_cdn_url`, including the original mirror rule. Restart the game and
inspect its requests: it must request the new patch hash from this repository.
Existing cached resources may mean a restart does not download anything.
Do not erase all game data just to refresh the cache.

The configuration pins a specific asset commit. No Node server or Render service
is needed. A visible menu or an activation label is not proof that features work.
If loading fails or gameplay is unstable, disable this experimental rule and
import `proxypin-rollback-v1.json` to restore the user-tested v1, or restore the
original `ff_client` ProxyPin rule. The client may require a resource
refresh to replace its cached experimental patch.

Fully close and relaunch the game when testing v2 so old in-flight requests cannot
survive a hot reload. Verify both the new patch hash and absence of key UI/requests
on the device. Static analysis only covers this payload, not other game networking.

## Validation
Run `python3 verify.py` in this repository. It checks all file sizes and SHA-256,
every manifest entry's compressed SHA-1, and the patch's GZIP/raw SHA-1.
These are structural integrity checks, not runtime or opcode validation.

Only the experimental patch and manifest differ from the baseline assets.
No backups, captured request headers, credentials or license-server tokens are
included. This mirror does not emulate a license server.