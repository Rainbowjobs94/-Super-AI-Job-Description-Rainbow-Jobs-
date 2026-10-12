---
name: hab-agent-monica
description: Prepare bounded Monica AI copy/paste tasks and reviewed API integration plans. Use for Monica at monica.im, multi-model drafting or Monica handoffs; not the unrelated Monica personal CRM.
---

# Monica AI handoff

1. Identify Monica AI at monica.im, not monicahq.com or similarly named services.
2. Start with a manual task packet: goal, allowed inputs, exact output, evidence
   requirements, zero-added-spend limit, prohibited actions and stop conditions.
3. Send only public or explicitly approved data. Do not forward a biography,
   private repo, skill library, wallet key or uploaded source by default.
4. For API work, reread official quickstart, available models, pricing and rate
   limits. The reviewed quickstart documents a funded balance requirement and
   openapi.monica.im/v1/chat/completions; this is not configured access.
5. Provision API credentials through the host's secret store. Never paste them
   into a skill, workflow JSON, browser frontend or repository.
6. Require explicit cost/data-sharing approval before the first remote call.
   Bound response size, retries, time and scope. Stop when budget is unknown.
7. Treat returned code as proposed; inspect, test and reconcile locally before
   applying it. No deployment, signing, trading or public posting authority.

## Copy/paste packet

Monica: perform [one goal] using [approved public sources]. Return [format]
with citations, assumptions and checks actually performed. Do not access other
accounts, run financial code, publish, deploy, spend or spawn further agents.
If an input/capability is missing, return the precise blocker and a manual
alternative. Do not request secrets in the response.

## Evidence

Reviewed official docs: https://platform.monica.im/docs/en/overview and
https://platform.monica.im/docs/en/quickstart (2026-10-10).
This module is guidance, not a Monica connection or tested agent installation.
