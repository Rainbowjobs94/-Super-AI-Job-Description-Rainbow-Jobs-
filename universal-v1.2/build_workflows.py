"""Build inactive n8n preparation templates; no provider calls or imported code."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".agents/skills/hab-n8n-control/workflows"
GUARD = r"""
const items = $input.all();
if (!Array.isArray(items) || items.length !== 1) throw new Error("Exactly one input required");
const d = items[0].json;
if (!d || typeof d !== "object" || Array.isArray(d)) throw new Error("Object input required");
const serialized = JSON.stringify(d);
if (serialized.length > 262144) throw new Error("Input exceeds character budget");
if (!["public", "synthetic"].includes(d.data_classification)) throw new Error("Only public or synthetic input is supported");
if (/"(?:private_key|mnemonic|seed_phrase|api_key|password|authorization|cookie|access_token|decryption_key)"\s*:/i.test(serialized)
 || /\b(?:sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b/.test(serialized)
 || /-----BEGIN [^-]*PRIVATE KEY-----/.test(serialized))
 throw new Error("Possible credential input rejected; use a secret manager");
if (d.approved === true || d.authorized === true) throw new Error("Input booleans do not authorize execution");
if (d.provider_spend_budget !== undefined && d.provider_spend_budget !== 0) throw new Error("Preparation templates support zero added provider spend only");
const envelope = {schema:"hab-preparation/1", mode:"PREPARATION_ONLY", execution_enabled:false,
 provider_calls_enabled:false, financial_actions_enabled:false, provider_spend_budget:0};
"""

TEMPLATES = [
    ("01-github-source-intake", "GitHub source intake",
     {"text": "https://github.com/agalwood/Motrix\nhttps://github.com/aria2/aria2", "data_classification": "public"},
     r"""
if (typeof d.text !== "string") throw new Error("text is required");
const pattern = /(?:https?:\/\/|git@)(?:www\.)?(?:github\.com[:/]|raw\.githubusercontent\.com\/)([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)/gi;
const repos = new Map();
const reserved = new Set(["settings","search","topics","features","orgs","users","marketplace","login"]);
for (const m of d.text.matchAll(pattern)) {
 const owner=m[1], repo=m[2].replace(/\.git$/i,"").replace(/\.+$/,"");
 if (reserved.has(owner.toLowerCase()) || !repo) continue;
 const id=(owner+"/"+repo).toLowerCase();
 if (!repos.has(id)) repos.set(id,{slug:owner+"/"+repo,url:"https://github.com/"+owner+"/"+repo});
 if (repos.size>200) throw new Error("Repository count exceeds budget");
}
return [{json:{...envelope, repositories:[...repos.values()], next:"Review metadata, pinned revision, README/license/manifests and nested skills before proposing a wrapper. No fetch/install performed."}}];
"""),
    ("02-skill-wrapper-draft", "Skill wrapper draft",
     {"name": "reviewed-repo-guidance", "description": "Review a specific repository before adapting its documented integration.",
      "repo": "owner/repo", "files_read": ["README.md", "LICENSE"], "data_classification": "synthetic"},
     r"""
if (typeof d.name!=="string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(d.name) || d.name.length>64) throw new Error("Invalid skill name");
if (typeof d.description!=="string" || !d.description.trim() || d.description.length>1024) throw new Error("Invalid description");
if (typeof d.repo!=="string" || !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(d.repo) || d.repo.split("/").some(p=>p==="."||p==="..")) throw new Error("Invalid repository");
if (!Array.isArray(d.files_read) || !d.files_read.length || d.files_read.length>50) throw new Error("Selected files are required");
for (const p of d.files_read) {
 if (typeof p!=="string" || p.length>240 || p.startsWith("/") || p.includes("\\") || p.split("/").some(s=>s===".."||s==="."||!s)
 || !/^[A-Za-z0-9_./-]+$/.test(p) || /(^|\/)(?:\.env|profile\.md|credentials|secrets)(?:$|[./])/i.test(p)) throw new Error("Unsafe selected path");
}
const wrapper = "---\nname: "+d.name+"\ndescription: "+JSON.stringify(d.description)+"\n---\n\n# Reviewed repository guidance\n\nSource: https://github.com/"+d.repo+"\nStatus: PROPOSED; selected files are caller-reported, not independently read by this workflow.\n\nRead host instructions first. Inspect: "+d.files_read.join(", ")+".\nPreserve originals, verify rights and capabilities, then propose the smallest change.\nNo installer execution, provider activation, financial actions or release authority.\n";
return [{json:{...envelope,skill_name:d.name,proposed_wrapper:wrapper,files_reported:d.files_read,revision_status:"UNRESOLVED",installation_status:"NOT_INSTALLED"}}];
"""),
    ("03-individual-agent-handoff", "Individual agent handoff",
     {"provider": "monica", "goal": "Compare two public project documentation pages with citations.", "data_classification": "public"},
     r"""
const providers=["monica","manus","you-com","replit","claude","chatgpt","codex","gemini","perplexity","grok","cursor","other"];
if (!providers.includes(d.provider)) throw new Error("Unknown provider; review a new adapter separately");
if (typeof d.goal!=="string" || !d.goal.trim() || d.goal.length>2000) throw new Error("Bounded goal required");
const packet = ["Provider: "+d.provider, "Goal: "+d.goal, "Inputs: public/synthetic allowlist only.",
 "Return citations, assumptions, actual checks and blockers. Keep added provider spend zero.",
 "Do not publish, deploy, sign, mint, trade, handle custody, create accounts or spawn agents.",
 "Missing tools or permission: return the precise blocker and manual fallback."].join("\n");
return [{json:{...envelope,provider:d.provider,manual_packet:packet,credential_status:"NOT_CONFIGURED",sharing_status:"Requires owner review before remote use"}}];
"""),
    ("04-huggingface-research", "Hugging Face research preparation",
     {"candidates": ["huggingface/skills", "huggingface/smolagents"], "data_classification": "public"},
     r"""
if (!Array.isArray(d.candidates) || !d.candidates.length || d.candidates.length>10) throw new Error("One to ten candidates required");
const candidates=[...new Set(d.candidates)];
for (const id of candidates) if (typeof id!=="string" || !/^[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+$/.test(id) || id.split("/").some(s=>s==="."||s==="..")) throw new Error("Invalid candidate ID");
return [{json:{...envelope,candidates,repository_kind:"Must distinguish model/dataset/Space/GitHub library before fetching.",
 checklist:["Read the appropriate card or README","Record revision, license, limitations and retrieval date","Check hardware, privacy, remote-code and cost requirements","Separate reported benchmarks from measured results"],
 disabled:["weight downloads","remote-code execution","paid inference/jobs","private data upload"],evidence_status:"UNFETCHED"}}];
"""),
    ("05-human-review-queue", "Non-authorizing human review queue",
     {"request_id": "example-review-001", "action": "propose_skill_import", "data_classification": "synthetic"},
     r"""
const actions=["propose_skill_import","review_repo","review_handoff","review_revision","review_research"];
if (typeof d.request_id!=="string" || !/^[A-Za-z0-9_-]{1,80}$/.test(d.request_id)) throw new Error("Opaque request ID required");
if (!actions.includes(d.action)) throw new Error("Action outside advisory allowlist");
return [{json:{...envelope,request_id:d.request_id,action:d.action,state:"PENDING_HUMAN_REVIEW",
 authorization_receipt:null,requires:["Authenticated human owner","Exact source/input digests","Capability/data/budget review","Host-enforced revocation and expiry"],
 warning:"This ticket neither authorizes nor executes an action; it is not a durable approval service."}}];
"""),
    ("06-revision-check-preparation", "Revision check preparation",
     {"previous": "snapshots/previous.json", "current": "snapshots/current.json", "output": "review.json", "data_classification": "synthetic"},
     r"""
for (const key of ["previous","current","output"]) {
 const p=d[key];
 if (typeof p!=="string" || p.length>180 || !/^[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*\.json$/.test(p)
 || p.split("/").some(s=>s===".."||s===".")) throw new Error("Safe relative JSON path required");
}
if (new Set([d.previous,d.current,d.output]).size!==3) throw new Error("Output must be separate");
return [{json:{...envelope,requires:"Installed canonical Hab CLI and reviewed local snapshots",
 argv:["python","-m","src.hab.cli","reconcile",d.previous,d.current,"--output",d.output],
 execution_status:"NOT_EXECUTED",notes:["Use argv, not a concatenated shell command","Compare actual revision hashes","Missing source is not a deletion instruction","Retain existing-file refusal and release holds"]}}];
"""),
    ("07-credit-checkpoint-plan", "Credit and checkpoint preparation",
     {"goal": "Inspect one repository and prepare a reviewed skill wrapper.", "max_reads": 20, "max_retries": 1, "data_classification": "public"},
     r"""
if (typeof d.goal!=="string" || !d.goal.trim() || d.goal.length>2000) throw new Error("Bounded goal required");
if (!Number.isInteger(d.max_reads) || d.max_reads<1 || d.max_reads>50) throw new Error("Read limit must be 1..50");
if (!Number.isInteger(d.max_retries) || d.max_retries<0 || d.max_retries>2) throw new Error("Retry limit must be 0..2");
return [{json:{...envelope,goal:d.goal,max_reads:d.max_reads,max_retries:d.max_retries,workers:1,
 strategy:["Inspect existing source first","Hash-based reuse","Targeted spans","Batch independent reads","Checkpoint before limits"],
 checkpoint_fields:["opaque task ID","source digests","completed checks","next action","holds","permission expiry"],
 platform_credit_usage:"UNKNOWN; not guaranteed zero",prohibited:["metering bypass","identity rotation","keep-alive evasion","unbounded model fan-out"]}}];
"""),
]


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, title, sample, code in TEMPLATES:
        doc = {
            "name": "Hab v1.2 — " + title + " [manual preparation]",
            "active": False,
            "nodes": [
                {"id": "manual", "name": "Manual Trigger", "type": "n8n-nodes-base.manualTrigger",
                 "typeVersion": 1, "position": [0, 0], "parameters": {}},
                {"id": "sample", "name": "Edit sample input", "type": "n8n-nodes-base.code",
                 "typeVersion": 2, "position": [260, 0], "parameters": {
                     "mode": "runOnceForAllItems", "language": "javaScript",
                     "jsCode": "const userInput = " + json.dumps(sample, indent=2) + ";\nreturn [{json:userInput}];"}},
                {"id": "prepare", "name": "Prepare bounded output", "type": "n8n-nodes-base.code",
                 "typeVersion": 2, "position": [520, 0], "parameters": {
                     "mode": "runOnceForAllItems", "language": "javaScript", "jsCode": GUARD + code}},
            ],
            "connections": {
                "Manual Trigger": {"main": [[{"node": "Edit sample input", "type": "main", "index": 0}]]},
                "Edit sample input": {"main": [[{"node": "Prepare bounded output", "type": "main", "index": 0}]]},
            },
            "settings": {"executionOrder": "v1", "executionTimeout": 60,
                         "saveDataErrorExecution": "none", "saveDataSuccessExecution": "none",
                         "saveManualExecutions": False},
            "pinData": {},
        }
        path = OUT / (stem + ".json")
        with path.open("x") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")


if __name__ == "__main__":
    build()
