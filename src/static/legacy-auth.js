/* Keep the legacy UI, but require operator access for its API requests too. */
(() => {
  const originalFetch = window.fetch.bind(window);
  let token = "";
  window.fetch = (url, options={}) => {
    const parsed = new URL(typeof url==="string"?url:url.url,location.href);
    if(parsed.origin===location.origin && parsed.pathname.startsWith("/api/")){
      const headers=new Headers(options.headers);
      headers.set("Authorization",`Bearer ${token}`);
      return originalFetch(url,{...options,credentials:"omit",headers});
    }
    return originalFetch(url,options);
  };
  window.addEventListener("DOMContentLoaded",()=>{
    const bar=document.createElement("div");
    bar.style.cssText="position:fixed;bottom:0;left:0;right:0;background:#182a29;padding:10px;z-index:1000;display:flex;gap:10px;align-items:center;color:white";
    const label=document.createElement("label");label.textContent="IA Guardian Hab operator token ";
    const input=document.createElement("input");input.type="password";input.autocomplete="off";label.append(input);
    const button=document.createElement("button");button.textContent="Unlock legacy APIs";
    button.onclick=()=>{token=input.value;input.value="";if(typeof loadFiles==="function")loadFiles();};
    const link=document.createElement("a");link.href="/";link.textContent="Return to Hab";link.style.color="white";
    bar.append(label,button,link);document.body.append(bar);
  });
})();
