const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const assert = require('node:assert/strict');
const dir=path.resolve(__dirname,'../.agents/skills/hab-n8n-control/workflows');
const files=fs.readdirSync(dir).filter(f=>f.endsWith('.json')).sort();
assert.equal(files.length,20);
let checks=0;
function run(code,data) {return vm.runInNewContext('(function(){\n'+code+'\n})()',{$input:{all:()=>data}},{timeout:1000});}
function codeFor(prefix) {return JSON.parse(fs.readFileSync(path.join(dir,files.find(f=>f.startsWith(prefix))))).nodes[2].parameters.jsCode;}
const item=d=>[{json:{data_classification:'synthetic',...d}}];
for(const file of files) {
 const flow=JSON.parse(fs.readFileSync(path.join(dir,file)));
 assert.equal(flow.active,false);assert.equal(flow.nodes.length,3);
 for(const node of flow.nodes) {assert.ok(['n8n-nodes-base.manualTrigger','n8n-nodes-base.code'].includes(node.type));assert.equal(node.credentials,undefined);}
 const sample=run(flow.nodes[1].parameters.jsCode,[{}]),code=flow.nodes[2].parameters.jsCode;
 const result=run(code,sample);
 assert.equal(result[0].json.execution_enabled,false);assert.equal(result[0].json.provider_calls_enabled,false);
 assert.equal(result[0].json.financial_actions_enabled,false);assert.equal(result[0].json.provider_spend_budget,0);checks++;
 for(const bad of [[],[{json:{...sample[0].json,data_classification:'private'}}],
 [{json:{...sample[0].json,approved:true}}],[{json:{...sample[0].json,authorized:true}}],
 [{json:{...sample[0].json,api_key:'synthetic-rejected'}}],
 [{json:{...sample[0].json,provider_spend_budget:1}}],
 [{json:{...sample[0].json,extra:'x'.repeat(262145)}}],
 [{json:{...sample[0].json}},{json:{...sample[0].json}}]]) {
  assert.throws(()=>run(code,bad));checks++;
 }
}
assert.throws(()=>run(codeFor('08'),item({target:'unknown',revision:'x'})));checks++;
assert.throws(()=>run(codeFor('09'),item({environments:['staging'],credential_refs:['https://a?key=foo']})));checks++;
assert.throws(()=>run(codeFor('10'),item({question:'x',depth:'unbounded',source_hints:['public']})));checks++;
assert.throws(()=>run(codeFor('11'),item({asset_ids:['opaque'],confidentiality:'anything'})));checks++;
assert.throws(()=>run(codeFor('12'),item({asset_ids:['opaque']})));checks++;
assert.throws(()=>run(codeFor('13'),item({mark:'x',goods_services:[],jurisdiction:'UNSPECIFIED'})));checks++;
assert.throws(()=>run(codeFor('14'),item({public_topic:'x',jurisdiction:'x',privateKey:'synthetic-rejected'})));checks++;
assert.throws(()=>run(codeFor('15'),item({jurisdictions:[],activities:['x'],data_types:['x']})));checks++;
assert.throws(()=>run(codeFor('16'),item({symptom:'' ,revision:'x'})));checks++;
assert.throws(()=>run(codeFor('17'),item({asset_symbols:['x'],network:'rogue'})));checks++;
assert.throws(()=>run(codeFor('18'),item({extension:'.exe',media_type:'application/json'})));checks++;
assert.throws(()=>run(codeFor('19'),item({roles:['admin@example.com']})));checks++;
assert.throws(()=>run(codeFor('20'),item({topic:'x',geography:'x',start_date:'2026-02-30',end_date:'2026-03-31'})));checks++;
assert.throws(()=>run(codeFor('20'),item({topic:'x',geography:'x',start_date:'2026-03-31',end_date:'2026-03-01'})));checks++;
const patent=run(codeFor('14'),item({public_topic:'public topic',jurisdiction:'UNSPECIFIED'}))[0].json;
assert.equal(patent.jurisdiction_hold,true);assert.equal(patent.novelty_verified,false);assert.equal(patent.filing_enabled,false);checks++;
const format=run(codeFor('18'),item({extension:'.habflow',media_type:'application/vnd.lt.habflow+json'}))[0].json;
assert.equal(format.parser_implemented,false);assert.equal(format.sample.payload.execution_enabled,false);
assert.equal(format.proposed_schema.additionalProperties,false);checks++;
console.log(JSON.stringify({status:'PASS',workflow_count:20,logic_checks:checks,
 scope:'All authored local JS snippets/JSON structure; no actual n8n import, external research or deployment performed'}));
