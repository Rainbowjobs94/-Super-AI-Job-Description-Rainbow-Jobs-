# Release scope and comparisons

| Requested area | v1.1 delivered | Deferred / disabled | Useful path now |
|---|---|---|---|
| Hab identity | Branded UI and master skill | GitHub slug unchanged | Existing repository history retained |
| Archive everything | Content-addressed intake, originals, member manifests | Infinite/million ZIP generation | One package per unique source, deterministic rebuilds |
| Pictures/documents | Original bytes and hashes preserved | OCR, PDF visual interpretation engine | Use host document/image tools with reviewed sources |
| Code/services/contracts | Stored, inspectable, exportable | Automatic execution of arbitrary uploaded code | Owner reviews mappings and runs relevant tests |
| Project transfers | Mapping, preview, approved apply, rollback | Autonomous cross-project writes | Explicit local owner-controlled sync |
| Revision refresh | Bounded offline hash/timestamp comparisons; private source overlays | Background fetching, automatic rebasing or merging | Compare default/feature/project snapshots; review changed or unavailable sources |
| Feature/task descriptions | Manual evidence-tagged registry | Full automatic feature inference | Agent reads selected source with recorded evidence |
| Duplicate code | Source/object SHA-256 dedup, aliases | Semantic equivalence guarantees | Compare hashes then review differences |
| Duplicate deployments | Candidate chain/address/role uniqueness | Live factory/pool/wallet indexing | Read-only deployment reconciliation before chain writes |
| Smart-contract migration | Transfer infrastructure | Actual contract/state/token migration | Sandbox compilation and migration tests after reconciliation |
| QuickSwap/pools/reserves | Registry boundaries | New liquidity, reserves, pools, vaults | Verify existing deployed identities and funding |
| Quantum/entropy/PoW/PoV | Preserved specifications; unverified proof format | New consensus or working mining network | Explicit threat model and independently testable protocol |
| Zero-data/ZK mining | Privacy boundary; no false ZK claim | Working ZK circuit/verifier | Choose statement/circuit and prove testnet correctness |
| Value acknowledgment | Unsigned consent/contribution record | Value/price/redemption guarantees | Collect evidence without making financial certification |
| Tax deductions/legal | Dated evidence fields and review gates | Eligibility, enforceability, regulatory certification | Qualified jurisdiction-specific review |
| Current research | Manual URL/date registry | Recurring verified primary-source refresh | Approve scheduler/provider access and source set |
| General AI | Deterministic local candidate extraction | Paid models/multi-provider orchestration | Portable agent handoff with scoped context |
| Run-on/unspaced requests | Raw input retained, candidates flagged | Guaranteed interpretation of arbitrary unspaced language | Confirm high-consequence ambiguities |
| Credits | Bounded persistent planning units and checkpoints | Unlimited credits or suspension avoidance | Zero-added-model-spend operation |
| Skills | Master + four companions + owner-private reference snapshot | Automatic installation on every host | Register master, search index, selectively open modules |
| Security | Bearer APIs, bounded intake, restricted previews | Production certification/multi-tenant auth | Provision secret/TLS and independently review release |
| Review/migration choices | Explicit gains/losses/fallback references | Treating every requested capability as already implemented | Review this matrix and guide before release |

None of the disabled capabilities are silently represented as working buttons.
Private library license rights remain unreviewed; its inclusion is for the owner's
reference, not public redistribution. Two reference modules have secret-like
instructional blocks redacted, with source/export hashes in the library index.
