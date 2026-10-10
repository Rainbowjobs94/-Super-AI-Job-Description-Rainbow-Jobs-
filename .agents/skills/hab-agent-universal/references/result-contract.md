# Result and checkpoint contract

Return goal, source/revision map, changed paths, tests with command and result,
blocked/disabled work, data-sharing/spend status, rollback and next action.
Use OBSERVED, SOURCE_CLAIM, PROPOSED, IMPLEMENTED, TESTED, UNAVAILABLE,
BLOCKED and CONFLICT distinctly. DEPLOYED needs a live target and verification.

Checkpoint: task ID, source digests, completed checks, next bounded action,
unresolved decisions, budget known/unknown and permission expiry.
Do not store secrets, raw prompts, private file bodies or profiling data in
checkpoint receipts. In a private approved source store, maintain source bodies
separately with their access controls.

Efficiency: search before reading, reuse hashes, retrieve selected spans, batch
independent reads, cap retries, use one worker by default and stop at a genuine
task boundary. No guarantee of zero platform credit usage, unlimited runtime or
suspension immunity. Do not evade plan limits or rotate identities.

Mode receipt: requested main mode Free; actual mode unknown unless reported by
the host. Preserve completed checks and revisions. A failed Free pass produces
a bounded Power handoff only for the unresolved slice, with reason and unknown/
known budget. There is no unconditional paid review or Max fallback. A local
planning label does not change Replit's selector or a provider billing tier.
