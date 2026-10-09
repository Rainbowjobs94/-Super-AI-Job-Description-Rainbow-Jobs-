/* Operator token stays only in memory and is sent only to same-origin /api paths. */
(() => {
  "use strict";
  const el = id => document.getElementById(id);
  let token = "", sources = [], busy = false;
  const actions = ["upload","export","parse","refresh","save-record","preview"];
  function notice(text, error=false) { el("notice").textContent=text; el("notice").className=error?"error":""; }
  async function api(path, options={}) {
    if (!path.startsWith("/api/")) throw new Error("Unsupported API path");
    const response = await fetch(path, {...options, credentials:"omit", headers:{...options.headers, Authorization:`Bearer ${token}`}});
    if (!response.ok) {
      const body=await response.json().catch(()=>({}));
      throw new Error(body.message || `Request failed (${response.status})`);
    }
    return response;
  }
  async function json(path, body) {
    return (await api(path, body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})).json();
  }
  function render() {
    const list=el("source-list"); list.replaceChildren();
    el("source-count").textContent=sources.length;
    el("file-count").textContent=sources.reduce((n,s)=>n+s.entries.length,0);
    el("flag-count").textContent=sources.reduce((n,s)=>n+s.entries.filter(e=>e.flags.length).length,0);
    if (!sources.length) { const p=document.createElement("p");p.textContent="No sources yet. Import a reviewed file to begin.";list.append(p); }
    for (const source of sources) {
      const row=document.createElement("label");row.className="source";
      const check=document.createElement("input");check.type="checkbox";check.value=source.id;check.setAttribute("aria-label",`Select ${source.aliases.join(", ")}`);
      const details=document.createElement("div"),title=document.createElement("strong"),meta=document.createElement("small"),hash=document.createElement("small");
      title.textContent=source.aliases.join(" / ");meta.textContent=`${source.entries.length} files · ${source.license_status} · ${source.evidence}`;
      hash.textContent=source.id;details.append(title,meta,hash);
      if(source.entries.some(e=>e.flags.length)){const flag=document.createElement("small");flag.className="flag";flag.textContent="Restricted entries will be excluded from export";details.append(flag);}
      row.append(check,details);list.append(row);
    }
  }
  async function load(){sources=(await json("/api/hab/catalog")).sources;render();}
  async function run(work) {
    if(busy)return;busy=true;
    try{await work();}catch(error){notice(error.message,true);}finally{busy=false;}
  }
  el("unlock").onclick=()=>run(async()=>{
    token=el("token").value;el("token").value="";
    await load();actions.forEach(id=>el(id).disabled=false);
    notice("Operator connected. Private catalog is available in this tab.");
  });
  el("lock").onclick=()=>{token="";location.reload();};
  el("upload").onchange=()=>run(async()=>{
    const file=el("upload").files[0];if(!file)return;
    const form=new FormData();form.append("file",file);
    await api("/api/hab/intake",{method:"POST",body:form});
    await load();notice("Imported and cataloged. No uploaded code was executed.");el("upload").value="";
  });
  el("export").onclick=()=>run(async()=>{
    const source_ids=[...document.querySelectorAll(".source input:checked")].map(c=>c.value);
    if(!source_ids.length)throw new Error("Select at least one source");
    const response=await api("/api/hab/export",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({source_ids})});
    const url=URL.createObjectURL(await response.blob()),a=document.createElement("a");
    a.href=url;a.download="ia-guardian-hab-source-bundle.zip";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    notice("Bundle exported. Check its manifest exclusions and redistribution holds.");
  });
  el("parse").onclick=()=>run(async()=>{
    const data=await json("/api/hab/parse",{message:el("request").value,request_id:crypto.randomUUID()});
    el("plan-output").textContent=JSON.stringify(data.result,null,2);
    notice("Candidates extracted locally; no execution authorized.");
  });
  el("refresh").onclick=()=>run(async()=>{el("record-output").textContent=JSON.stringify((await json(`/api/hab/records/${el("kind").value}`)).records,null,2);});
  el("save-record").onclick=()=>run(async()=>{
    const result=await json(`/api/hab/records/${el("kind").value}`,JSON.parse(el("record").value));
    el("record-output").textContent=JSON.stringify(result.record,null,2);notice("Record saved. Evidence status is not a live verification.");
  });
  el("preview").onclick=()=>run(async()=>{
    const result=await json("/api/hab/merge-preview",{source_id:el("source-id").value,mappings:JSON.parse(el("mappings").value)});
    el("merge-output").textContent=JSON.stringify(result,null,2);notice("Preview only. No destination files changed.");
  });
})();
