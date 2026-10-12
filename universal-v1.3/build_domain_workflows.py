"""Add thirteen authored no-network preparation workflows; preserve 01-07."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hab_authored_workflow_base", ROOT / "universal-v1.2/build_workflows.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)  # Our own inert definitions, not uploaded code.
OUT = ROOT / ".agents/skills/hab-n8n-control/workflows"
HELPERS = r"""
function label(v, field, limit=500) {
 if (typeof v!=="string" || !v.trim() || v.length>limit) throw new Error("Invalid "+field);
 return v;
}
function list(v, field, limit=20) {
 if (!Array.isArray(v) || !v.length || v.length>limit) throw new Error("Invalid "+field);
 return [...new Set(v.map(x=>label(x,field,200)))];
}
const extra = JSON.stringify(d);
if (/"(?:private[-_]?key|api[-_]?key|seed[-_]?phrase|access[-_]?token|decryption[-_]?key)"\s*:/i.test(extra))
 throw new Error("Credential field rejected");
"""
DOMAIN_TEMPLATES = [
    ("08-deployment-review", "Deployment readiness and rollback",
     {"target": "staging", "revision": "reviewed-source-revision", "data_classification": "synthetic"},
     r"""
if (!["development","staging","testnet","production","mainnet"].includes(d.target)) throw new Error("Unknown deployment target");
const revision=label(d.revision,"revision",100);
return [{json:{...envelope,target:d.target,reported_revision:revision,revision_verified:false,state:"RELEASE_REVIEW_REQUIRED",
 checklist:["Identify actual target and deployed configuration","Inspect existing automatic merge/deploy triggers","Verify tests and migration/backup/restore plan","Prepare staging health and denial checks","Record exact rollback and release owner","Obtain exact target/revision deployment approval","Verify live health before claiming deployed"],
 production_hold:["production","mainnet"].includes(d.target),deployment_executed:false}}];
"""),
    ("09-environment-audit", "Environment and credential-reference audit",
     {"environments": ["development","staging"], "credential_refs": ["secret-manager:operator"], "data_classification": "synthetic"},
     r"""
const environments=list(d.environments,"environments",5);
if (environments.some(x=>!["development","staging","testnet","production","mainnet"].includes(x))) throw new Error("Unknown environment");
const refs=list(d.credential_refs,"credential_refs",10);
if (refs.some(x=>!/^[A-Za-z][A-Za-z0-9_:/.-]{2,120}$/.test(x))) throw new Error("Opaque credential references required");
return [{json:{...envelope,environments,credential_references:refs,secret_values_received:false,
 checklist:["Separate public config and credential values","Confirm least privilege and expiry","Rotate/revoke through secret manager","Test synthetic secret redaction and access denial","Verify HTTPS, data retention, backup/restore and emergency pause"],
 configuration_observed:false,provisioning_enabled:false}}];
"""),
    ("10-research-evidence-brief", "Standard or deep research brief",
     {"question": "Compare public agent-skill import standards.", "depth": "deep", "source_hints": ["primary documentation","original studies"], "data_classification": "public"},
     r"""
const question=label(d.question,"question",2000);
if (!["standard","deep"].includes(d.depth)) throw new Error("Depth must be standard or deep");
const hints=list(d.source_hints,"source_hints",10);
return [{json:{...envelope,question,depth:d.depth,source_hints:hints,max_queries:d.depth==="deep"?8:3,queries_executed:0,
 steps:["Define scope, dates and inclusion/exclusion criteria","Search primary sources first","Read selected sources and record provenance","Build claim/source/design/sample/limitations matrix","Record contradictions, confidence and evidence gaps","Cite load-bearing claims; separate reported and tested"],
 extra_deep_checks:d.depth==="deep"?["Independent cross-check","Sensitivity to study selection","Unknown/contested conclusions"]:[],
 current_information_status:"NOT_RETRIEVED"}}];
"""),
    ("11-ip-security-provenance", "IP security and provenance",
     {"asset_ids": ["synthetic-asset-001"], "confidentiality": "confidential", "data_classification": "synthetic"},
     r"""
const ids=list(d.asset_ids,"opaque asset IDs",20);
if (!["public","internal","confidential","restricted"].includes(d.confidentiality)) throw new Error("Unknown confidentiality class");
return [{json:{...envelope,opaque_asset_ids:ids,planned_confidentiality:d.confidentiality,
 checklist:["Inventory source rights and provenance","Keep source content in approved private storage","Threat-model access, egress and prompt injection","Review provider retention/training/data-sharing terms","Separate signing secrets from source and manifests","Record hashes without claiming ownership or legal clearance","Review patent-sensitive disclosure before public release"],
 actual_storage_controls_verified:false,ownership_verified:false,confidential_content_requested:false}}];
"""),
    ("12-copyright-license-review", "Copyright, license and assignment review",
     {"asset_ids": ["synthetic-source-module"], "jurisdiction": "UNSPECIFIED", "data_classification": "synthetic"},
     r"""
const ids=list(d.asset_ids,"asset IDs",20), jurisdiction=label(d.jurisdiction,"jurisdiction",100);
return [{json:{...envelope,asset_ids:ids,jurisdiction,jurisdiction_hold:jurisdiction==="UNSPECIFIED",
 matrix_columns:["asset/source/revision","claimed author/owner","license/notice","assignment evidence","third-party and AI-generated material","redistribution obligations","evidence/reviewer/status"],
 checklist:["Preserve source and license notices","Do not assume a hash proves ownership","Distinguish permission to read, modify and redistribute","Review copyleft/attribution and assets separately","Escalate ambiguous ownership or terms to qualified counsel"],
 clearance_status:"NOT_ESTABLISHED",filing_enabled:false,legal_advice:false}}];
"""),
    ("13-trademark-search-brief", "Trademark research preparation",
     {"mark": "Synthetic Example Mark", "goods_services": ["software"], "jurisdiction": "UNSPECIFIED", "data_classification": "synthetic"},
     r"""
const mark=label(d.mark,"mark",200), goods=list(d.goods_services,"goods/services",10), jurisdiction=label(d.jurisdiction,"jurisdiction",100);
return [{json:{...envelope,proposed_mark:mark,goods_services:goods,jurisdiction,
 checklist:["Choose applicable official trademark registers","Search similar words, spellings and relevant classes","Record owners/status/dates and source links","Consider unregistered rights and territories","Obtain qualified clearance before adoption or filing"],
 searches_performed:0,jurisdiction_hold:jurisdiction==="UNSPECIFIED",registration_or_clearance:"NOT_ESTABLISHED",filing_enabled:false}}];
"""),
    ("14-patent-prior-art-brief", "Patent and prior-art research preparation",
     {"public_topic": "Public provenance-record workflows", "jurisdiction": "UNSPECIFIED", "data_classification": "public"},
     r"""
const topic=label(d.public_topic,"public nonconfidential topic",1000), jurisdiction=label(d.jurisdiction,"jurisdiction",100);
return [{json:{...envelope,public_topic:topic,jurisdiction,
 checklist:["Review disclosure/confidentiality boundaries before research","Search official patent databases and primary literature","Record filing/priority dates, families, claims and legal status","Map proposed elements to prior art without inventing claims","Separate novelty, inventiveness and freedom-to-operate questions","Route to patent counsel before disclosure/filing decisions"],
 searches_performed:0,jurisdiction_hold:jurisdiction==="UNSPECIFIED",novelty_verified:false,freedom_to_operate:"NOT_ESTABLISHED",filing_enabled:false}}];
"""),
    ("15-legal-compliance-matrix", "Jurisdiction and compliance issue matrix",
     {"jurisdictions": ["UNSPECIFIED"], "activities": ["software service"], "data_types": ["public metadata"], "data_classification": "synthetic"},
     r"""
const jurisdictions=list(d.jurisdictions,"jurisdictions",10), activities=list(d.activities,"activities",10), types=list(d.data_types,"data types",10);
return [{json:{...envelope,jurisdictions,activities,data_types:types,
 matrix_columns:["activity/entity/jurisdiction","potential obligation","authoritative source and date","applicability reasoning","evidence/control","review owner","unknown/hold"],
 checklist:["Identify actual entity, users and jurisdictions","Review privacy, consumer, IP and sector-specific rules","Distinguish accounting credits, tokens, payments and regulated activities","Separate tax questions from claimed proofs","Use current primary sources and qualified review","Do not evade disclosure/access rules"],
 authoritative_sources_read:0,compliance_certified:false,legal_advice:false,jurisdiction_hold:jurisdictions.includes("UNSPECIFIED")}}];
"""),
    ("16-debugging-plan", "Evidence-first debugging",
     {"symptom": "Synthetic import rejected because root SKILL.md is absent.", "revision": "unverified-example", "data_classification": "synthetic"},
     r"""
const symptom=label(d.symptom,"redacted symptom",2000), revision=label(d.revision,"revision",100);
return [{json:{...envelope,reported_symptom:symptom,reported_revision:revision,
 steps:["Reproduce and record exact inputs/environment","Inspect relevant code, issue history and existing fixes","Separate observations from hypotheses","Run discriminating bounded checks","Propose minimal fix preserving current behavior","Run targeted tests and observe outcome","Record remaining uncertainty and rollback"],
 cause_confirmed:false,fix_applied:false,checks_executed:0}}];
"""),
    ("17-protocol-invariants-review", "Protocol, asset and pool invariants",
     {"asset_symbols": ["RC","Shift SC","Soul SC"], "network": "testnet", "data_classification": "synthetic"},
     r"""
const symbols=list(d.asset_symbols,"asset symbols",20);
if (!["off-chain","testnet","mainnet","unknown"].includes(d.network)) throw new Error("Unknown network classification");
return [{json:{...envelope,reported_asset_symbols:symbols,network:d.network,
 checklist:["Resolve symbol collisions by chain/address/role","Verify units, decimals, caps, mint/burn/vault rights and maturity","Compare actual contract/ledger versions and state machines","Reconcile pools/reserves/treasuries before adding duplicates","Separate activity, issuance, collateral, price and settlement","Distinguish ML-KEM cryptography from mining KEM","Test invariants with synthetic inputs; retain unknown owner decisions"],
 chain_state_observed:false,contracts_compiled:false,economic_rules_changed:false,
 disabled:["deployment","mint/burn/vault/signing","balance changes","automatic expiration/exclusion","pool or treasury changes"]}}];
"""),
    ("18-file-format-design", "File format and schema proposal",
     {"extension": ".habflow", "media_type": "application/vnd.lt.habflow+json", "data_classification": "synthetic"},
     r"""
if (typeof d.extension!=="string" || !/^\.[a-z][a-z0-9]{1,15}$/.test(d.extension) || [".exe",".dll",".sh",".py",".js",".bat"].includes(d.extension)) throw new Error("Non-executable proposed extension required");
if (typeof d.media_type!=="string" || !/^application\/(?:json|vnd\.[a-z0-9.-]+\+json)$/.test(d.media_type)) throw new Error("JSON media type required");
const proposed_schema={$schema:"https://json-schema.org/draft/2020-12/schema",type:"object",additionalProperties:false,
 required:["schema_version","id","payload"],properties:{schema_version:{const:"1"},id:{type:"string",minLength:1,maxLength:80},payload:{type:"object"}}};
return [{json:{...envelope,proposed_extension:d.extension,proposed_media_type:d.media_type,registration_status:"PROPOSED_NOT_REGISTERED",
 proposed_schema,sample:{schema_version:"1",id:"synthetic-example",payload:{kind:"advisory-workflow",execution_enabled:false}},
 checklist:["Define encoding, byte limits and parser behavior","Reject executable/path traversal content","Specify compatibility and migration","Test schema/parser with malformed inputs","Define signature semantics separately"],
 parser_implemented:false,cryptographic_or_legal_proof:false}}];
"""),
    ("19-role-access-matrix", "Role and separation-of-duties matrix",
     {"roles": ["owner","operator","researcher","reviewer"], "data_classification": "synthetic"},
     r"""
const roles=list(d.roles,"roles",12);
if (roles.some(x=>!/^[a-z][a-z0-9-]{1,39}$/.test(x))) throw new Error("Role labels required, not personal/account identifiers");
return [{json:{...envelope,proposed_roles:roles,
 matrix:roles.map(role=>({role,proposed_scope:"read approved metadata and prepare bounded artifacts",implemented:false,self_escalation:false,financial_permission:false})),
 checklist:["Map capabilities to least privilege and data scope","Separate author/reviewer/release approver","Require authenticated owner and expiring permissions","Enforce server-side checks and revocation","Test denied access and emergency pause"],
 roles_granted:false,authorization_service_implemented:false}}];
"""),
    ("20-market-analysis-trends", "Market analysis and trends research",
     {"topic": "Public creator-platform adoption", "start_date": "2026-01-01", "end_date": "2026-10-10", "geography": "UNSPECIFIED", "data_classification": "public"},
     r"""
const topic=label(d.topic,"topic",1000), geography=label(d.geography,"geography",100);
for (const key of ["start_date","end_date"]) {
 if (typeof d[key]!=="string" || !/^\d{4}-\d{2}-\d{2}$/.test(d[key])) throw new Error("ISO date required");
 const parsed=new Date(d[key]+"T00:00:00Z");
 if (!Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0,10)!==d[key]) throw new Error("Invalid date");
}
if (d.start_date>d.end_date) throw new Error("Date range reversed");
return [{json:{...envelope,topic,geography,start_date:d.start_date,end_date:d.end_date,
 matrix_columns:["metric/units","source/as-of date","coverage/sample/method","current vs historical values","confounders/uncertainty","claim and evidence"],
 checklist:["Select primary public data and define metrics","Check source freshness, methods and survivorship bias","Compare trends with seasonality and uncertainty","Use scenarios rather than guaranteed forecasts","Separate market evidence from token backing or financial returns"],
 market_data_retrieved:false,forecast_guaranteed:false,personalized_investment_advice:false,trading_enabled:false}}];
"""),
]


def build():
    for stem, title, sample, code in DOMAIN_TEMPLATES:
        doc = {
            "name": "Hab v1.3 — " + title + " [manual preparation]", "active": False,
            "nodes": [
                {"id": "manual", "name": "Manual Trigger", "type": "n8n-nodes-base.manualTrigger",
                 "typeVersion": 1, "position": [0, 0], "parameters": {}},
                {"id": "sample", "name": "Edit sample input", "type": "n8n-nodes-base.code",
                 "typeVersion": 2, "position": [260, 0], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript",
                 "jsCode": "const userInput = " + json.dumps(sample, indent=2) + ";\nreturn [{json:userInput}];"}},
                {"id": "prepare", "name": "Prepare bounded output", "type": "n8n-nodes-base.code",
                 "typeVersion": 2, "position": [520, 0], "parameters": {"mode": "runOnceForAllItems", "language": "javaScript",
                 "jsCode": base.GUARD + HELPERS + code}},
            ],
            "connections": {
                "Manual Trigger": {"main": [[{"node": "Edit sample input", "type": "main", "index": 0}]]},
                "Edit sample input": {"main": [[{"node": "Prepare bounded output", "type": "main", "index": 0}]]},
            },
            "settings": {"executionOrder": "v1", "executionTimeout": 60, "saveDataErrorExecution": "none",
                         "saveDataSuccessExecution": "none", "saveManualExecutions": False},
            "pinData": {},
        }
        with (OUT / (stem + ".json")).open("x") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")


if __name__ == "__main__":
    build()
