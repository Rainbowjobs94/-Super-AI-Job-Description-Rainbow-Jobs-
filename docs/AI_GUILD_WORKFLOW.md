# AI Guild workflow: proposed coordination, not live autonomy

## Status and scope

This playbook consolidates the requested AI Guild Orchestrator role and the
build, review, update, debugging, blockchain/mining research, security patch,
and database workflows from the documentation PRs listed below.

These are proposed operating procedures, not evidence that this application
connects to models, runs autonomous guilds, tunes mining hardware, applies
migrations, or deploys code. The implemented Hab source-management tools and
their manual approval boundaries remain authoritative. See [HAB_GUIDE.md](HAB_GUIDE.md).
The historical Physical-23 profile is context, not additional execution authority.

## Build a bounded guild

1. Record the goal, canonical repository revision, relevant existing PRs,
   allowed files, data classification, acceptance tests, and stop conditions.
2. Reuse local tools for discovery and static analysis first. Examples include
   a code indexer, Semgrep, linters, and an available local model. These are
   examples, not installed dependencies or permission to execute imported code.
3. Separate the update, review, and verification roles. An implementation
   proposes a patch, a reviewer checks logic and risks, and the verification
   step records actual build and regression results.
4. Escalate to an external model or paid tool only with approved access,
   data handling, and spending limits. A free tool is not permission to send
   private source externally; paid execution is not automatically necessary.
5. Publish only a real, inspected diff on an isolated branch. If the requirement
   is already satisfied, report that in the existing task instead of opening
   another no-diff PR.

Frameworks such as LangChain, CrewAI, or AutoGen and enterprise analysis tools
can be evaluated later. No framework, provider, premium model, or autonomous
execution engine is activated by this document.

## Review and update

- Preserve the current owner's work and compare against the current main
  revision, not a stale task snapshot.
- Reproduce bugs with synthetic fixtures, add a failing regression test, make
  the smallest correction, and record exact commands and outcomes.
- Review source-write restrictions, authentication, data exposure, compatibility,
  migrations, accessibility, and deployment triggers before publication.
- Use CI to fail honestly. A passing check is not a human review or release
  approval; do not approve or merge an agent's own changes automatically.
- Update prompts, models, tool versions, and vulnerability data only after
  comparing results against a fixed evaluation set. Record versions, evidence,
  decisions, and limitations without credentials or private source in reports.
- Stop repeated unsuccessful attempts and report the evidence and blocker.
  Do not regenerate equivalent branches, repeat no-op tasks, or manufacture
  changes merely to reduce an open-PR count.

## Domain workflows

- **Code debugging and builds:** index the relevant call path, reproduce the
  failure, patch locally, and run targeted tests plus affected build checks.
  Staging deployment is a separate approved operation, not a CI side effect.
- **Blockchain and mining research:** use local test fixtures, static contract
  analysis, and explicitly authorized testnets to evaluate logic, gas use,
  throughput, memory, and economic assumptions. Hardhat, Slither, or Mythril
  are possible tools, not proof of protocol safety or financial value.
  Hardware monitoring may inform a recommendation; no automatic overclocking,
  power-limit changes, pool switching, signing, minting, trading, or mainnet
  deployment is authorized.
- **Security patches:** verify advisory applicability, isolate the vulnerable
  path, propose a targeted patch, and run regression and scoped defensive
  security tests. Dynamic tests or adversarial tools require an authorized
  isolated target. Neither a model nor a scanner can guarantee security or
  approve its own patch for production.
- **Database maintenance:** profile authorized read-only queries and use
  synthetic or approved staging data for SQL/index/schema proposals. Review
  locking, data-loss risks, backups, restore verification, rollback, retention,
  and any off-peak maintenance window before separately approving migrations,
  archival, optimization jobs, or production application.

## Source PRs and reconciliation

This consolidated playbook retains the common requested scope from #31, #34,
#37, #38, #40, #41, #43, #45, #47, #49, #50, #52, #74, #84, and #120.
Their branches and review history remain available. Conflicting prose variants
are not concatenated into the application, and claims of already implemented
autonomous capability are deliberately not adopted without implementation
evidence. Audit issue #283 records the queue cleanup and replacement PR.
