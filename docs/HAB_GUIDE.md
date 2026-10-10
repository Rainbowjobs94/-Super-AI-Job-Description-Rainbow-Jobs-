# IA Guardian Hab 1.1 — operator and portable toolkit

For current branch/project inventory comparison, use the offline `reconcile`
command described in [revision synchronization](REVISION_SYNC.md). Private
source and project-skill overlays are separate owner-only deliveries. They do
not automatically update a Replit checkout or install a source application.

This release upgrades the existing Flask hub and ships the same core as a
Python CLI. It is a tested local source-management control plane, not a complete
autonomous AI, new blockchain or live mining deployment.

## Run

Install `requirements.txt` in Python 3.10+ and configure `HAB_OPERATOR_TOKEN`
as a random, private value of at least 32 characters using your host's secrets
manager. Never commit it, include it in an export, or paste it into agent chat.
The browser password field sends it only to the same-origin server over HTTPS
and holds it only in the current tab. All operator APIs fail closed without it.

```
python -m src.hub
# production host command:
gunicorn --bind=0.0.0.0:5000 src.hub:app
# tests:
python -m unittest discover -s tests -v
```

Do not publicly deploy merely because local tests pass. Token provisioning,
TLS, host access, durable storage/backups and an independent security review
remain release prerequisites. This is a single trusted-operator system, not
multi-tenant user authentication.

Open `/` for Hab, `/legacy` for the preserved original workspace.
Current community metrics remain configuration-derived; they are not live
measurements of the user's external accounts.

## Source packages

```
python -m src.hab.cli --store data/hab ingest source.zip original.pdf
python -m src.hab.cli --store data/hab catalog
python -m src.hab.cli --store data/hab export SOURCE_ID --output source-bundle.zip
```

Input byte hashes deduplicate originals. Each original name remains an alias.
Archive members retain hashes, lengths, source IDs and privacy flags.
Raw originals remain private in the local object store. Exports exclude
restricted entries and contain a provenance/exclusions manifest.
Secret detection is heuristic, not a substitute for human secret review.
License status remains UNREVIEWED; private exports do not grant redistribution.

Limits: 16 MiB file/member, 64 MiB expanded archive/export, 4096 archive
entries, 100:1 compression ratio, 256 MiB object store. Web requests are limited
to 16 MiB including multipart overhead. Nested archives, encrypted entries,
symlinks, special files, traversal and portable path collisions are rejected.
Nonportable punctuation in archive member titles is encoded (e.g. colon becomes
`%3A`) in transfer paths while exact original member names remain in the manifest.
Original archive bytes are unchanged; encoded-path collisions are rejected.
PDF/DOCX text extraction is not implemented by this toolkit; preserve originals
and use the host's document-analysis capability separately.

## Merge and rollback

Create `mappings.json`, for example `{"src/helper.py":"src/helper.py"}`:

```
python -m src.hab.cli plan SOURCE_ID /explicit/destination \
  --mappings mappings.json --output reviewed-plan.json
python -m src.hab.cli apply reviewed-plan.json --approve EXACT_PLAN_HASH
# only when the conflicting changes were explicitly approved:
python -m src.hab.cli apply reviewed-plan.json --approve EXACT_PLAN_HASH --allow-conflicts
python -m src.hab.cli rollback --approve EXACT_PLAN_HASH
```

CLI commands run in the owner's local environment. Apply/rollback require a
POSIX advisory lock; unsupported platforms must not run them unlocked.
Do not edit destination files concurrently in another process. Advisory locking
coordinates Hab operations, not arbitrary external editors.
The source/destination snapshot is rechecked before writes. Interrupted writes
leave an APPLYING or FAILED journal. Review it and rollback instead of blindly
retrying. Rollback blocks if files changed after merge.
Empty directories created by a merge may remain after rollback.
Reviewed mappings cannot target dot-directories, private credentials or profiles.
Imported scripts and dependencies are never executed or installed automatically.

## Experimental portable formats

- `MANIFEST.ltpkg.json`: portable package/provenance manifest.
- Merge JSON with `format: ltmerge/1`: destination snapshot and approval hash.
- `.ltproof.json` with `format: ltproof/1`: unsigned contribution statement,
  asset hash and consent reference.

```
python -m src.hab.cli proof original.png \
  --acknowledgement "Participant acknowledges this contribution" \
  --consent "consent-record-id" --output contribution.ltproof.json
```

These are real schemas understood by Hab utilities. They are not new operating
system formats, signature schemes, enforceable obligations or proofs of economic
value. ltproof is explicitly not signed or zero-knowledge.

## Planning and shared records

`POST /api/hab/parse` takes `message` and an idempotency `request_id`.
Raw text is preserved; local keyword detection returns advisory candidates.
No model call, shell command or transaction is executed.
Local planning units are bounded by `HAB_PLANNING_LIMIT` (default 100).
Units persist in the store; the same key/input reuses its checkpoint at no
additional local planning cost. Different input with the same key is rejected.
These units are not dollars or Replit credits. No unlimited-credit promise.

Tasks, features, deployment candidates and research sources are manual records.
IMPLEMENTED/TESTED require evidence references, which still need human validation.
Deployments reject duplicate chain/address and chain/role records but do not
query RPCs, wallets, pool factories or real treasuries.
Research requires an HTTPS URL and retrieval date; it does not fetch the URL,
verify its contents or continuously monitor law/regulation changes.

## What changed / what remains

| Behavior | Before | Hab release |
|---|---|---|
| Operator API access | Anonymous | Required bearer token; unprovisioned returns 503 |
| Source upload | Could overwrite application files | Quarantine intake only; explicit CLI merge |
| Source write API | Unrestricted within project | Disabled by default; reviewed CLI recommended |
| File reads | Any project-contained file | Allowlisted roots, restricted paths/content blocked |
| Chat archive command | Generated sample code ZIP | Directs to real inspected catalog export |
| Historical archive builder | Legacy generator | Preserved in module/history, not promoted to deployment evidence |
| GitHub browser | Public source reader | Preserved behind operator access |
| AI planning | Keyword chat | Structured local candidates and idempotent budget checkpoints |
| Live contracts/mining | Unverified | Not enabled or altered |

Read the skills package's SKILL.md and import/register it in the target agent.
Agent services differ in file size, tools and permissions; uploading a ZIP
does not install skills or connect external systems automatically.

## Release holds / remaining roadmap

Automatic connector sync, recurring primary-source research, external model
generation, a full code/migration/dependency audit, real ZK circuits, new
consensus implementation, chain verification and settlement remain future work.
Do not reuse unauthenticated transaction-signing patches from source uploads.
Financial designs require unit/supply/pool/custody reconciliation, testnets,
independent security review and jurisdiction-specific qualified advice.
