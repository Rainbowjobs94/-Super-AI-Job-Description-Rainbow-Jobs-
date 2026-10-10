# OmniRoute — additive Hab source entry

Source: https://github.com/diegosouzapw/OmniRoute
Pinned commit: 7510677f2f8f5317f1947284dab650d01333915d
Observed package version: 3.8.52. Root license: MIT.

Entry point: ../.agents/skills/hab-omniroute/SKILL.md
Evidence and selected-source hashes:
../.agents/skills/hab-omniroute/references/source.json
Native module index:
../.agents/skills/hab-omniroute/references/native-skills.json
Portable directions:
../.agents/skills/hab-omniroute/references/copy-paste.md

This adds a gateway-planning branch to the skill tree without replacing any
existing source, skill, workflow, application or manifest. Native modules remain
references; no provider, installation or paid fallback is activated.
The prior v1.3 manifest and review findings are not repaired by this addition.

The selected-source download retains the complete 52-file upstream skills/
subtree plus seven pinned root documents/manifests, with hashes checked.
It does not contain the complete application, git history, private services,
an installed mobile app or a running gateway. The whole-repository recursive
response exceeded the connector's response-size bound; that limitation is
recorded rather than silently claiming a complete scan.

For eventual integration, extend the existing protected Hab source registry
and module selector through Task #5 after its prerequisites. Preserve all
original dependencies and holds. Stage changes in an isolated project copy;
do not merge main, deploy or send private data to external providers.
