# IA Guardian Hab 1.0 — verification and release holds

Date: 2026-10-09. Base GitHub main:
`5aa3103db6c95ee80dced6ee4dd2d1be1c8077c9`.

## Checks performed

- Python unittest: **72 tests passed**, including original community/content/
  GitHub tests and new archive, auth, integrity, merge, rollback, registry,
  malformed-input and budget tests.
- `compileall` checked source and scripts.
- JavaScript syntax checks passed for Hab and legacy authorization scripts.
- ZIP CRC, entry uniqueness and SHA-256 manifests passed for generated deliveries.
- All **19 per-source inspected packages** passed their content hashes.
- Public toolkit excludes uploaded originals and personal profile documents.
- The toolkit's own test suite is included; imported user code is not run.

## Source/private-snapshot accounting

Twenty uploaded files have nineteen unique original byte identities.
The private archive retains original bytes and all twenty name/hash mappings.
Eight source ZIPs contain 119 file members. Including the eleven unique
non-ZIP originals, the intake catalog contains 130 member/standalone entries.
One PDF was an exact duplicate; original aliases are preserved.

The private skill snapshot covers all **163 top-level SKILL.md files** present
under the platform/custom/secondary skill roots, plus their eligible references,
scripts and included license notices. Five new authored skills are supplied
separately. Secret-like instructional examples in two reference files are
redacted; the library index records source and exported hashes.
Connector-specific tool catalogs are host-dependent and not packaged as
portable credentials or promised cross-host tools.

## Browser/runtime limitation

An automated Chromium/Playwright smoke check was attempted but could not
complete in the conversation sandbox: missing shared libraries in the bundled
browser; incompatible/hanging system Chromium; attempted runtime adaptation
also failed. There is **no successful desktop/mobile browser-flow verification**
or visual sign-off. This is a release hold, not a confirmed application bug.
The reusable optional smoke script is included for a compatible host.

## Not claimed

No production deployment, repository slug rename, general AI provider calls,
recurring research, live chain verification, financial action, collateral,
tax deduction, price peg or real zero-knowledge/consensus protocol was enabled
or certified. Uploaded implementations and claims still need scoped review.
This is not a full audit of every imported service, contract or legal document.

Operator-token provisioning, HTTPS, durable storage/backups, browser verification
and independent security review remain prerequisites for public operation.
The local evidence registry is single-operator and manually reviewed.
