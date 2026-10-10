# Domain playbooks and artifact contracts

| Domain | Required metadata | Proposed artifacts | Operation still requires |
| --- | --- | --- | --- |
| GitHub source/sync | Repo, commit, selected paths, rights | Source crosswalk, skill wrapper, draft diff | Access, reviewed writes/PR, no auto-merge |
| Deployment | Target environment, source revision, health criteria | Release checklist, staging tests, migration/rollback plan | Exact deployment approval; live checks |
| Environment | Environment labels, credential references, owners | Configuration/rotation/recovery matrix | Secret manager and reviewed provisioning |
| Agent roles | Goal, actual tools, data class, limits | Scoped task packet and evidence receipt | Host-enforced capability/expiry/budget |
| Standard research | Question, dates, public sources | Search ladder, cited claims/contradictions | Approved fetches and source evaluation |
| Deep research | Above plus inclusion criteria | Evidence matrix, study/claim quality, gaps | Bounded query budget and independent review |
| IP security | Opaque assets, confidentiality class, provenance | Access/egress/licensing/threat checklist | Actual storage controls; owner/legal review |
| Copyright/license | Asset, claimed owner, source/license notices | License/assignment/source map and obligations | Rights verification and counsel where needed |
| Trademark | Proposed mark, goods/services, jurisdiction | Official-registry search brief/conflict log | Qualified clearance and separate filing decision |
| Patent | Public/nonconfidential invention brief, jurisdiction | Prior-art search plan, claim/source comparison | Patent counsel; no novelty/FTO guarantee |
| Compliance | Entity type, jurisdictions, activity/data types | Obligation/evidence/reviewer matrix | Current authoritative sources and qualified review |
| Debugging | Reproduction, environment, revision, redacted symptoms | Hypotheses, discriminating checks, minimal fix plan | Actual tests and observed outcome |
| Protocols | Chain/address/role, units/decimals/caps, versions | State machine, invariants, conflict/alias review | Testnet/live-chain checks and approval |
| File formats | Purpose, schema/version, content rights | JSON schema/sample, migration/validation rules | Actual parser, compatibility/security tests |
| Role/access matrix | Roles, data scopes, capabilities | Proposed RBAC/separation-of-duties matrix | Authenticated owner review and enforcement |
| Market/trends | Topic, date range, geography, units | Source/time/method matrix, scenarios/uncertainty | Current data; no automated financial actions |

## Additional branches

Use the deployment/environment playbooks for backup/restore drills and incident
recovery. Use IP/security and roles for defensive threat models and data
retention. Use source/deployment for dependency/SBOM/license updates and
cross-project compatibility; major version changes need separate review.
Use release checklists for accessibility, performance, privacy and public-claim
verification. These are scoped extensions, not additional activated services.

## Research/IP handling

Before confidential research, classify the material and verify source rights,
project access, provider retention/training terms and permitted data sharing.
Send only the minimum approved excerpt; otherwise use public/synthetic
metadata or local review. Keep raw contents and signing secrets off immutable
ledgers. Do not claim “zero data” while publishing sensitive hashes/identifiers.

Record chain of custody: source ID, actual digest, revision, acquisition method,
owner assertion, license/assignment evidence, access class and review status.
Keep assertions distinct from verified assignments or registrations.
Do not invent NDAs, consents, signatures, trademarks, patents or tax status.
Patent-sensitive material may require review before any public disclosure.

Preferred research starts with the relevant official registry/regulator,
statutory text and primary literature; record retrieval date and jurisdiction.
A saved portal link is not an actual search or current legal interpretation.
No filing fees, registry submissions, provider calls or disclosures are enabled.

## Format proposal

An extension alone creates no enforceable value or cryptographic proof. Define
media type, schema/version, required fields, byte limits, signature semantics,
backward compatibility and migration/validation rules. For proof-like formats,
separate unsigned provenance from independently verified signatures and real
zero-knowledge constructions. Never execute a file based on its extension.
