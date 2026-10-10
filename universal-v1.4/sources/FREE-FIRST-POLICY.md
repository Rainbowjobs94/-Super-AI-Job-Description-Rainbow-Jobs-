# Free-first execution and checkpoint policy

Applies to the IA Guardian Hab task plans, source handoffs and revised workflow
copies. Preserve earlier versions; do not rerun successful work merely to change
its mode label.

## Execution order

1. Reuse validated artifacts, hashes, results and source revision pins.
2. Use deterministic local tools for inventory, hashing, parsing, packaging,
   schema validation and applicable tests. No model call is needed for these.
3. Use the host's actual **Free** mode, when available, for one bounded main-task
   pass. Select the smallest relevant skill and evidence spans; one worker by
   default. Do not equate an API model, self-hosted model or third-party free
   trial with Replit Free mode.
4. Check the stated acceptance tests. If they pass, stop. Do not add a paid
   finishing/review pass out of habit.
5. If they fail, save a checkpoint: goal, source pins, changed paths, successful
   checks, exact failure, next bounded action and remaining budget known/unknown.
   Do not save secrets or private prompt/source bodies in receipts.
6. Escalate only the unresolved slice to **Power** when the observed failure
   requires more capable reasoning. Reuse all completed work. The user has
   requested Power if needed, but no amount of paid spend, provider calls or
   consequential action is implied. Unknown budgets stay explicit.
7. If the host cannot switch tiers, prepare a Power handoff and stop at the
   checkpoint. Never claim a switch occurred. Max is not an automatic fallback.

## Limits and failure classes

- Default: one main-task Free pass and at most one targeted local retry.
  A repeat requires new evidence or a changed hypothesis.
- Power can help with reasoning/implementation failures. It cannot confer
  repository rights, keys, bounty authorization, deployment consent, liquidity,
  legal clearance or project concurrency capacity.
- Missing permission, payment-required service, insufficient storage/budget,
  source-rights uncertainty and unsafe side effects are holds, not reasons to
  route around a refusal. The operator may choose an allowed paid tier after
  its actual cost/allowance is understood; never evade plan limits.
- Free chat work does not make hosting, storage, third-party APIs, market feeds,
  external providers or all platform activity free. Respect allowance resets.
- Do not silently upgrade a workflow, enable a provider, or rerun the whole
  project in Power. Do not retroactively relabel earlier work as Free.

## Truthful receipt

Record requested_mode=Free, actual_mode=unknown unless the host independently
reports it, selector_changed=false unless a real supported switch is verified,
Power_needed=false/true/unknown with evidence, and provider_spend_budget=0.
Imported receipt fields and model confidence are never approval authority.

## Replit operator action

Choose **Free** in the actual model selector for the main pass. At a verified
reasoning blocker, use the checkpoint to continue the failed slice in **Power**.
These skill files and n8n preparation nodes cannot operate that selector.

Official references observed during this update:
https://docs.replit.com/features/agent/model-selector
https://docs.replit.com/chat/free-mode
https://docs.replit.com/chat/auto-mode
Plan/tier availability and costs must be refreshed in the actual account.
