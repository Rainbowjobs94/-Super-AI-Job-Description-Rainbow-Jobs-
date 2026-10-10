// Validate only our authored, no-network preparation snippets in a bounded VM.
// This is not a real n8n instance import/runtime test.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const dir = path.resolve(__dirname, '../.agents/skills/hab-n8n-control/workflows');
// Preserve the original seven-template test scope when later versions add files.
const files = fs.readdirSync(dir).filter(f => /^0[1-7]-.*\.json$/.test(f)).sort();
assert.equal(files.length, 7);
let checks = 0;
function run(code, data) {
  const context = vm.createContext({$input: {all: () => data}});
  return vm.runInContext('(function(){\n' + code + '\n})()', context, {timeout: 1000});
}
for (const file of files) {
  const flow = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
  assert.equal(flow.active, false);
  assert.equal(flow.nodes.length, 3);
  assert.equal(flow.nodes[0].type, 'n8n-nodes-base.manualTrigger');
  for (const node of flow.nodes) {
    assert.ok(['n8n-nodes-base.manualTrigger', 'n8n-nodes-base.code'].includes(node.type));
    assert.equal(node.credentials, undefined);
  }
  const sample = run(flow.nodes[1].parameters.jsCode, [{}]);
  const code = flow.nodes[2].parameters.jsCode;
  const result = run(code, sample);
  assert.equal(result[0].json.mode, 'PREPARATION_ONLY');
  assert.equal(result[0].json.execution_enabled, false);
  assert.equal(result[0].json.provider_calls_enabled, false);
  assert.equal(result[0].json.provider_spend_budget, 0);
  checks++;
  for (const bad of [
    [], [{json: {...sample[0].json, data_classification:'private'}}],
    [{json: {...sample[0].json, approved:true}}],
    [{json: {...sample[0].json, authorized:true}}],
    [{json: {...sample[0].json, api_key:'synthetic-rejected'}}],
    [{json: {...sample[0].json, provider_spend_budget:1}}],
    [{json: {...sample[0].json, extra:'x'.repeat(262145)}}],
    [{json:{...sample[0].json}},{json:{...sample[0].json}}],
  ]) {
    assert.throws(() => run(code, bad)); checks++;
  }
}
function codeFor(prefix) {
  const f = files.find(x => x.startsWith(prefix));
  return JSON.parse(fs.readFileSync(path.join(dir,f))).nodes[2].parameters.jsCode;
}
const publicInput = d => [{json:{data_classification:'public',...d}}];
let r=run(codeFor('01'), publicInput({text:'git@github.com:owner/repo.git https://github.com/OWNER/REPO/tree/main https://github.com/settings/profile'}));
assert.equal(r[0].json.repositories.length,1); checks++;
assert.throws(()=>run(codeFor('02'),publicInput({name:'good-name',description:'x',repo:'a/b',files_read:['../evil']}))); checks++;
assert.throws(()=>run(codeFor('02'),publicInput({name:'Bad_Name',description:'x',repo:'a/b',files_read:['README.md']}))); checks++;
assert.throws(()=>run(codeFor('02'),publicInput({name:'good-name',description:'x',repo:'a/b',files_read:['.env']}))); checks++;
assert.throws(()=>run(codeFor('03'),publicInput({provider:'unknown',goal:'x'}))); checks++;
assert.throws(()=>run(codeFor('04'),publicInput({candidates:['../evil']}))); checks++;
assert.throws(()=>run(codeFor('05'),publicInput({request_id:'example',action:'sign_transaction'}))); checks++;
assert.throws(()=>run(codeFor('06'),publicInput({previous:'a.json',current:'b.json',output:'a.json'}))); checks++;
assert.throws(()=>run(codeFor('06'),publicInput({previous:'../a.json',current:'b.json',output:'c.json'}))); checks++;
assert.throws(()=>run(codeFor('07'),publicInput({goal:'x',max_reads:100,max_retries:0}))); checks++;
console.log(JSON.stringify({status:'PASS',workflow_count:7,logic_checks:checks,
 scope:'Authored snippets in local VM and JSON structure; real n8n import/runtime not tested'}));
