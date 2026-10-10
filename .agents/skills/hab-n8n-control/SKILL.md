---
name: hab-n8n-control
description: Prepare manual-first n8n source intake, skill normalization, provider handoffs, research, approval queues and revision checks. Use for semi-automation workflow JSON, credential wiring and human-controlled agent operations.
---

# n8n control handoff

## Defaults

The bundled workflows are inactive, manual-trigger, no-network preparation
templates. They perform local transformations of synthetic/approved inputs,
not remote provider calls or enforcement of financial authorization.

1. Inspect the target n8n version, installed node types and instance security.
2. Read `references/workflow-guide.md`, then import a single workflow JSON.
3. Edit the sample-input node using public or synthetic data. Do not paste keys,
   private-source bodies or raw profiles into inputs or saved execution history.
4. Execute manually and inspect the resulting plan. No scheduler/webhook or
   outbound execution is enabled by these templates.
5. Before adding HTTP/API nodes, verify documented schemas, credential type,
   allowlisted endpoint, privacy consent, budget, timeout and rate limits.
6. Require a real authenticated human approval service for consequential
   actions; do not trust an approved boolean in input JSON.
7. Add durable idempotency, uncertain-result reconciliation, bounded retries,
   cancellation, redacted receipts and capability revocation in the host.
8. Test failure/denial cases and exact target-instance imports before activation.

Credentials live in n8n credentials or the server's secret manager, never in
workflow JSON, SKILL.md, logs or source. Preserve existing workflows by importing
new versioned copies rather than overwriting active flows.

No live trading, betting, signing, minting, custody, deployment or provider spend
is authorized. Manual export/import is not proof of a running n8n integration.

## Expanded library

The v1.3 collection adds thirteen domain-specific preparation templates to the
seven original workflows. Read `references/domain-workflows.md` to select one.
All twenty remain inactive/manual/no-network. Confidential research uses
synthetic or public metadata only in these templates; do not paste the research
contents into saved execution inputs. A private-data workflow needs separately
reviewed instance/storage controls before use.
