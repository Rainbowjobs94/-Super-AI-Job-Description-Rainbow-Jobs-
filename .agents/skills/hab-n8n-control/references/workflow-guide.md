# Seven manual-first workflow templates

| Template | Preparation output | Still disabled |
| --- | --- | --- |
| GitHub source intake | Normalized explicit repo references | Fetch/clone/install |
| Skill wrapper draft | Valid proposed frontmatter and source map | Auto-activation/overwrite |
| Individual agent handoff | Host-specific bounded task packet | Provider requests/spend |
| Hugging Face research | Card-reading research checklist | Model downloads/remote code |
| Human review queue | Non-authorizing review ticket | Approval/execution/signing |
| Revision check preparation | Canonical Hab CLI reconciliation plan | Shell/API execution |
| Credit/checkpoint plan | Bounded local-first work plan | Quota bypass/credit guarantee |

Each JSON uses one Manual Trigger v1 and Code v2 preparation nodes.
These node versions were checked against n8n's source. JSON structure and local
Code logic are tested separately; importing/running them in a real n8n instance
still requires an instance-specific check.

Node map: Manual Trigger → Edit sample input → Prepare bounded output.
The output does not contain an executable approval or provider dispatch.

Import: select a workflow JSON in n8n's import UI, retain a new workflow name,
confirm inactive state and node compatibility, edit only approved inputs and
run manually. Compare the output with the stated contract.

Post-import checks: default dry-run; no credentials embedded; no schedules,
webhooks, shell or HTTP nodes; missing/invalid inputs rejected; budget zero;
no approved=true shortcut; private/secret inputs rejected or kept out of logs.

For a future live connection, use HTTP Request nodes and n8n credentials after
explicit review; Code node sandbox network access is not assumed. Do not copy
an uploaded shell/Python script into a Code/Execute Command node.

Retention and retries: configure the target instance not to retain sensitive
execution inputs; cap attempts and polling; reconcile uncertain upstream writes.
There is no persistent approval store or scheduler in these templates.
