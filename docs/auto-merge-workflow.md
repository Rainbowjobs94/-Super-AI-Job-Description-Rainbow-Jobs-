# Controlled, fail-closed automatic merges

Auto-merge remains enabled only after a repository owner approves the exact
current PR head through GitHub's review control. The approval is the **Start**
action: it applies to that commit, not to later revisions. The separate
`PR Quality Checks` workflow runs with read-only permissions, checks out the
exact candidate SHA without persistent credentials, and runs the tests.

The privileged `Auto Review, Test, and Merge PRs` workflow starts only from a
successful completion of that trusted quality workflow. It does not check out
PR code. Before merging, it rechecks the owner approval, the exact head and
base SHAs, current PR state, all check runs, commit
statuses, and other workflow runs. The merge API call is pinned to the approved
head SHA. Errors, missing data, unknown mergeability, and pending or failed
checks stop the merge.

## Operator controls

- **Start:** the owner approves the current head commit in the PR review UI.
- **Pause:** apply `operator:hold` (or another configured hold label). Removing
  the label resumes eligibility only if approval and every other gate still
  pass.
- **Stop:** close the PR or apply `operator:stop`. The persistent label keeps
  it blocked until an operator deliberately removes it; reopening a closed PR
  does not bypass the remaining gates.

These controls use GitHub's review and label UI; they do not add a separate
Replit Start/Pause/Stop dashboard or a continuously running agent.

## Audit record and release prerequisites

Commits and PR review history record the changed revisions and approvals.
GitHub Actions records each validation and merge-gate run, including the
candidate SHA and final outcome. This workflow does not post PR comments. GitHub
may still generate its own email, push, or workflow notifications; this change
does not guarantee silence for those platform notifications. Similarity
analysis is not implemented as an automated check in this patch.

The workflow token cannot read repository administration settings, so this
patch does not claim to inspect branch-protection configuration. GitHub itself
enforces any configured branch protection or rulesets on the final SHA-pinned
merge request; a rejected merge fails the run. The workflow also independently
requires its own successful quality job, a fresh owner approval for the exact
head, and successful check/status/workflow results. This patch does not change
repository settings or branch protection.

The existing Build & Lint workflow is not treated as proof of passing tests.
This workflow runs the test suite directly and propagates failures. A merge to
`main` may trigger existing deployment workflows; this change is not deployment
authorization. Existing unsafe workflow copies on other branches require
separate review and repair.
