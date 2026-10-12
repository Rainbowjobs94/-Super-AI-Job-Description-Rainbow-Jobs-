# IA Guardian Hab universal skill addendum v1.2

This addendum preserves the five prior Hab skills and adds nine dedicated
modules. It includes seven inactive, no-network n8n preparation workflows.
It does not install a provider, publish a project or activate financial services.
The core skill's CLI examples require the corresponding Hab runtime; this
skill-only pack is not a standalone installation of that runtime.

## Use the smallest format

- Copy/paste: read COPY-PASTE.md and one module.
- Native skill: choose an individual module ZIP containing SKILL.md at root.
- Whole tree: use the portable root-loader bundle or copy its skills directories
  into the target host's documented skill location.
- n8n: import one workflow, inspect its node types and inactive state, then
  test synthetic input. Local checks are not a real n8n instance import test.
- GitHub: use a reviewed source revision and the import module. Missing root
  SKILL.md means inspect README/docs/nested skills and propose a wrapper,
  not “this source has no usable information.”

For Replit workspace-wide use, upload the chosen skills through workspace
Knowledge → Skills. Authoring files here does not automatically install them
into other conversations, projects or providers.

## Preserved and excluded

Original uploads, older archives, source hashes and existing skill modules remain
unchanged. Conflicting versions are cataloged, not erased. Raw source uploads,
biographies, private project snapshots, credentials and provider memory are
excluded from the shareable pack; their private evidence index is separate.
No source installer, uploaded program or trading bot was executed.

The universal packet supports manual handoff to other individual agents; it is
not a promise every service supports native skill imports. Provider names,
authentication and budgets must be checked on each receiving host.
Read FEATURE-COMPARISONS.md for what each choice gains or leaves disabled,
and RESEARCH-NOTES.md for dated official-source observations.

## Capability progression

Local/read-only preparation → proposed wrapper/change → human review →
bounded integration tests → separately approved operation/release.
Read-only preparation cannot approve its own execution or financial actions.
