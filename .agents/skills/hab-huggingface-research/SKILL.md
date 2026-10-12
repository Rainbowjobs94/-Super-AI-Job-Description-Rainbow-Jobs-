---
name: hab-huggingface-research
description: Research Hugging Face model cards, datasets, Spaces, agent skills and smolagents with revision, license, safety and cost checks. Use for HF discoveries and model/provider comparisons without automatically downloading weights or running remote code.
---

# Hugging Face research

1. Define the task, output quality needs, hardware and zero-added-spend limit.
2. Inspect model/dataset/Space cards and README metadata first. Record repo ID,
   exact revision when available, license, intended use, limitations, evaluation
   sources, resource requirements, access restrictions and retrieval date.
3. Distinguish models, datasets, executable Spaces, skills and code libraries.
   A Space may run arbitrary code; a model card is not an independent audit.
4. Compare a few task-relevant candidates, not the entire Hub. Mark paper
   claims and benchmark claims as reported until independently tested.
5. Do not download weights, launch paid jobs/Spaces, upload private datasets,
   enable telemetry or set trust_remote_code=True by default.
6. Prefer reviewed non-executable formats; inspect code and pin revisions
   before loading any model/tool. Treat pickle and remote code as execution.
7. If installing HF skills, inspect the chosen folder/manifest and host setup.
   Native import is host-specific; manual Markdown remains the fallback.
8. Provide a cited comparison and a synthetic evaluation plan. State costs and
   runtime availability as unknown unless measured or currently documented.

## First-party research entry points

- https://huggingface.co/docs/hub/model-cards
- https://huggingface.co/docs/hub/agents
- https://github.com/huggingface/skills
- https://github.com/huggingface/smolagents
- https://github.com/huggingface/diffusers

These sources were read or metadata-checked on 2026-10-10. No model weights,
training job, provider inference or agent runtime was installed or tested.

Output columns: candidate/revision, task fit, license evidence, resources,
privacy/egress, execution risk, reported evaluation, measured evaluation,
cost status and proposed next step.
