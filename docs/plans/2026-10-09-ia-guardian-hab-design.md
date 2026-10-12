# IA Guardian Hab — approved dual delivery

User approval: upgrade existing hub and deliver the portable toolkit (“Do both”).
Repository slug rename, publication of uploaded sources, mainnet actions and
paid provider calls are excluded.

## Architecture

Preserve the Flask/community modules and GitHub read-only browser. Add one
standard-library Python package shared by Flask routes and a CLI. Store imported
objects by SHA-256 and provenance records in SQLite. Validate ZIP boundaries
before importing bytes. Never run imported code or install its dependencies.

Deliver a compact agent skill plus versioned domain reference skills, private
workspace skill snapshot and private attachment archive. Public code contains
no attachment bytes, personal profile or connector credentials.

## Acceptance criteria and sequence

1. Reconcile against GitHub main at 5aa3103db6c95ee80dced6ee4dd2d1be1c8077c9.
2. Implement bounded content-addressed intake, archive checks, secret-location
   flags, provenance aliases, package manifests and deterministic ZIP exports.
3. Implement explicit merge mappings with dry-run statuses, content-based plan
   approval, exclusive apply lock and rollback journal; no web apply endpoint.
4. Add persistent tasks, budget checkpoints, local request candidate extraction,
   deployment candidate uniqueness and manually reviewed research records.
5. Protect all operator APIs with a provisioned server-side bearer secret;
   disable unprotected legacy writes. Keep source reads private.
6. Add responsive Hab operator UI and preserve legacy UI behind authentication.
7. Test malicious archives, duplicate input, corrupt objects, merge conflicts,
   interruption recovery, auth failure, malformed requests and budget blocking.
8. Export toolkit, skills and private archive; create a draft PR, never merge it.

## Limits

Local task extraction is deterministic and advisory, not a general AI model.
Unspaced language is ambiguous; preserve it and request clarification when needed.
Deployment and research registry entries are candidate records, not live checks.
No automatic project sync, recurring research, ZK circuits or settlement is
claimed. The registry and reviewed merge workflow provide manual synchronization.
Cryptographic hashes establish byte integrity, not market value or legal rights.
Budget limits apply to local planning units; provider billing is unknown.

## Rollback

Keep legacy module history. Merge application writes only approved paths after
checking the original plan. Journal old and new hashes; restore originals only
if the destination has not changed since the recorded write. Failed operations
leave a journal for recovery. A partial/failed operation is never reported as
complete.
