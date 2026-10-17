# Agent coordination and PR safety

Read the current README, docs/HAB_GUIDE.md, relevant source, and existing open
PRs before changing this repository. Preserve the current IA Guardian Hab
security boundaries and concurrent owner work.

- If the requested feature already exists and there is no file diff, report
  that finding in the original task. Do not open another verification-only PR.
- Inspect `git diff` before publishing. A PR described as "no changes" must not
  contain source edits. Verification scripts must use temporary fixtures, never
  overwrite real project files, and restore patched application configuration.
- Chat must not write source files. Keep legacy writes disabled by default,
  uploads in quarantine, operator authentication, and reviewed merge approvals.
- Do not replace an application file with a verification placeholder or bring
  obsolete pre-Hab upload implementations back into the current app.
- Work on an isolated branch. No force-pushes, branch deletion, automatic merge,
  production launch, security-check suppression, or artificial queue reduction.
- Run `python -m pip install -r requirements-dev.txt`, fatal lint checks, and
  `python -m unittest discover -s tests -v`. Report failures honestly.
- PR verification is read-only. A passing check is not owner review or
  deployment evidence. Obtain specific approval for merge and production work.

Audit context: issue #283 documents repeated Jules-generated zero-diff PRs and
misleading verification PRs. Closing them does not stop recurring tasks at Jules.
Deduplicate or pause those tasks at their source rather than generating new PRs.
