# Minimal OmniRoute handoff

Copy only this packet plus the relevant native module, not the entire library:

> Task: Plan a bounded OmniRoute integration for the current project.
> Source: diegosouzapw/OmniRoute, commit
> 7510677f2f8f5317f1947284dab650d01333915d, observed version 3.8.52.
> Read the current project instructions and hab-omniroute first.
> Preserve every existing module and provider adapter.
> Select one module from references/native-skills.json; retrieve its pinned
> source only if the host has a supported reader.
> Compare docs-only, isolated gateway and existing-endpoint adapter options.
> Explain what each enables, leaves disabled, costs and requires.
> Keep provider calls, paid fallback, installation, tunnels and deployment off.
> No secrets in chat or source; use the actual host secret manager.
> Zero added provider spend. Stop on permission/eligibility/quota failures.
> Do not confuse third-party free routes with Replit Free mode.
> Produce a small implementation plan, acceptance tests and a checkpoint.
> Do not claim this packet installed a gateway or switched the host model.

## Import

The Hab wrapper ZIP has SKILL.md at its root, with relative references/.
Register it through the target host's supported skill import mechanism.
Host format validation and capabilities vary; import success is not activation.

The separate selected-source ZIP retains the upstream skills/ tree and seven
root documents byte-for-byte with license/notices and hash evidence. It is a
reference collection, not a one-click app or one root-level native skill.
Choose a single upstream skill folder, include applicable notices and relative
resources, validate it for the target host, and review its instructions before use.
Do not auto-install all 46 native modules.
