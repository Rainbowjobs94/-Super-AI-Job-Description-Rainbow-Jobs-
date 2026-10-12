# Version-aware source reconciliation

Hab is the portable operator/source-transfer toolkit, not automatically the
canonical blockchain consensus repository. A project's consolidation decision
can select another repository without deleting or replacing this toolkit.

## Check both GitHub and Replit

- Resolve the exact default branch, relevant feature branch and current pull
  request head. `pushed_at` and a project's last-updated timestamp are discovery
  hints, not proof of changes to the default branch.
- Inspect current Replit HEAD separately. An environment can have newer work
  than GitHub, or remain older than a draft PR. Never infer synchronization.
- Preserve staged, unstaged and untracked work. When a read-only status check
  cannot run, report working-tree state as unknown rather than clean.
- Pin imported export manifests separately from the current project revision.
  A manifest's older source revision is not automatically equivalent to HEAD.
- Store owner-private repository inventories, code and proposal documents
  outside the public toolkit. Keep project-scoped skill versions and references
  together; do not replace global instructions with imported source instructions.

## Offline comparison

Produce JSON snapshots using schema `hab-revisions/1`, a timezone-aware
`observed_at`, and a bounded `sources` list. Each source has a stable `id`, a
complete `revision` hash and `status: OBSERVED`. Represent missing access,
empty repositories and unresolved sources with `UNAVAILABLE`, `EMPTY` or
`BLOCKED` and a null revision. Include branch names in identities.

```sh
python -m src.hab.cli reconcile previous.json current.json --output review.json
```

The CLI reads at most 256 KiB per input, accepts at most 200 source identities,
rejects duplicates and invalid observation times, and refuses to overwrite
an existing output. It does not create the intake store or contact a provider.

`NEW` and `CHANGED` require review. `UNAVAILABLE` never means deleted.
Stale observations (24 hours by default), future observations, empty repositories
and inaccessible sources block automatic conclusions. Historical baseline
timestamps are retained; only current observations are age-gated.

**No automatic fetch, merge, scheduling, signing, deployment or financial action.**
A comparison does not verify ancestry, source correctness, test results,
contract runtime, circulating supply, liquidity, tax treatment or legal rights.

## Compatibility rules before merging

- Match assets by chain and address, not symbol. Two contracts can both use SC
  but have different names, decimals, roles and rights.
- Preserve global supply ceilings separately from daily mint limits, circulating
  supply, lifetime issuance and proposed payout subdivisions.
- Preserve revised liquidity-layer names and proposal status within their source
  project. A newer economic proposal does not silently replace deployed tokens.
- Preserve activation holds, source/runtime mismatch findings, authoritative
  backend choices, paused registration and project-specific release gates.
- Treat consensus version targets and unchecked readiness checklists as plans,
  not implemented, audited, deployed or approved release states.
- Reuse existing split source packages when available. Inspect every part and
  its combined manifest; a guide/index ZIP does not contain the whole app.
- Prefer pinned lockfiles and each workspace's own package manager. Dependency
  fixes in one TypeScript workspace do not justify copying lockfiles into another
  application or changing this Python toolkit's dependency set.
