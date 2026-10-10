# Bounded public-source research notes

Observed 2026-10-10; this is not a permanent freshness guarantee.

## Providers

- Monica AI: official overview/quickstart document a funded API balance and
  openapi.monica.im/v1/chat/completions. Do not confuse Monica AI with the
  unrelated Monica CRM. No first-party Monica skill repo was established.
  Sources: https://platform.monica.im/docs/en/overview and
  https://platform.monica.im/docs/en/quickstart.
- Manus: official docs currently lead to API v2, with v1 deprecated. Verify
  exact authentication/task/webhook reference before implementing.
  Sources: https://manus.im/docs/integrations/manus-api and
  https://open.manus.im/docs.
- You.com: official agent docs and youdotcom-oss/agent-skills include host-specific
  integrations. Requests/queries may leave the host for You.com. The old
  TypeScript SDK path is deprecated; recheck documented current alternatives.
  Sources: https://you.com/docs/agents and
  https://github.com/youdotcom-oss/agent-skills.

## Hugging Face

Research section entry points: cards, agent docs, native skills and code-agent
library. Cards expose intended use/limits/license/evaluation metadata; they are
not independent certification. The official skills repo includes skill folders
and an AGENTS.md fallback; smolagents may execute generated code and needs a
reviewed execution boundary. Diffusers is an additional source-file reference.
No inference benchmark, model install, training job or live HF integration ran.

Sources:
https://huggingface.co/docs/hub/model-cards
https://huggingface.co/docs/hub/agents
https://github.com/huggingface/skills
https://github.com/huggingface/smolagents
https://github.com/huggingface/diffusers

## Repository differences that affect reuse

Motrix's current README describes the v2 beta, a new MDXP core and unvalidated
v1 settings migration. Do not silently treat an old download-manager prompt as
tested current behavior. aria2 is a CLI/RPC program with README.rst and COPYING,
not a root native skill.
https://github.com/agalwood/Motrix
https://github.com/aria2/aria2

K-Dense-AI/claude-skills-mcp's README says it is no longer maintained/hosted.
Preserve the reference; do not select it as a freshly maintained default.
https://github.com/K-Dense-AI/claude-skills-mcp

AutoGen's README states maintenance mode and points new users to Microsoft
Agent Framework; existing AutoGen work remains a separate preserved branch.
https://github.com/microsoft/autogen
https://github.com/microsoft/agent-framework

n8n declares Sustainable Use and Enterprise licenses. aria2 and Slither have
copyleft licensing metadata. Rights must be reviewed per intended use; an
unclassified license field does not mean unrestricted or “no license.”
https://github.com/n8n-io/n8n
https://github.com/aria2/aria2
https://github.com/crytic/slither

Public redirect observations retain aliases:
modelcontextprotocol/experimental-ext-skills → modelcontextprotocol/ext-skills;
supabase-community/supabase-mcp → supabase/mcp.
These do not establish replacements for every unavailable reference.
