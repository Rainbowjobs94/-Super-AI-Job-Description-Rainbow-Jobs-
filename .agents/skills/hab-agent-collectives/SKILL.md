---
name: hab-agent-collectives
description: Plan controlled multi-agent collaboration with nonoverlapping roles, evidence receipts and budget limits. Use for agent collectives, LangGraph, CrewAI, Microsoft Agent Framework or legacy AutoGen handoffs; not blanket autonomy.
---

# Bounded agent collective

1. Use one coordinator. Delegate only independent work that justifies extra
   cost; no model fan-out for simple reads. Keep one writer per path.
2. Give each worker goal, exact input allowlist, output contract, budget,
   permissions, stop conditions and prohibited capabilities.
3. Separate source research, implementation and review roles. A reviewer never
   grants its own release approval. A model cannot increase its own permissions,
   spawn additional workers, change economic rules or activate a provider.
4. Retain provenance and source hashes; reconcile results before merging.
   Handle stale outputs, retries and duplicate work with task IDs and leases.
5. Require host-enforced authorization, cancellation and emergency stop.
   An advisory prompt is not an implemented policy gateway or sandbox.
6. Inspect dependency versions, licenses, telemetry, callbacks and tool-execution
   defaults before installing any framework. Unknown costs block execution.
7. Use local tests and explicit human approval for consequential changes.

## Framework research references

- https://github.com/langchain-ai/langgraph
- https://github.com/crewAIInc/crewAI
- https://github.com/microsoft/agent-framework
- https://github.com/microsoft/autogen

The observed AutoGen README states maintenance mode and points new users to
Microsoft Agent Framework. Preserve existing AutoGen work; propose migration
separately rather than silently replacing it. Metadata availability is not a
benchmark or proof these frameworks fit the current project.

Default roles: source reader → bounded implementer → independent evidence
review → human owner. Use manual packets if no controlled runtime exists.
