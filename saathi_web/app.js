"use strict";
const $ = s => document.querySelector(s);
let csrf = "", current = null, busy = false;
const node = (tag, value) => { const n = document.createElement(tag); if (value !== undefined) n.textContent = value; return n; };
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:"POST", headers:{"Content-Type":"application/json", "X-Saathi-CSRF":csrf}, body:JSON.stringify(body)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error?.message || "Request failed. Refresh saved state before retrying.");
  return result;
}
async function run(action) {
  if (busy) return;
  const focused = document.activeElement;
  busy = true;
  document.querySelectorAll("button").forEach(b => {b.disabled = true;});
  $("#status").textContent = "Working with mock data…";
  try { await action(); $("#status").textContent = "Saved locally. All results are explicitly mocked."; }
  catch (e) { $("#status").textContent = e.message; }
  finally { busy = false; document.querySelectorAll("button").forEach(b => {b.disabled = false;}); if(document.activeElement===document.body && focused?.isConnected) focused.focus(); }
}
function button(label, action, style="secondary") { const b=node("button",label);b.type="button";b.className=style;b.addEventListener("click",()=>run(action));return b; }
async function history() {
  const tasks=await api("/api/tasks"), list=$("#history"); list.replaceChildren();
  if(!tasks.length) list.append(node("p","Your first mock task will appear here."));
  for(const t of tasks) list.append(button(`${t.status} · ${t.payload.intent?.city || "Details needed"} · ${t.payload.intent?.date || "Date needed"}`,async()=>show(await api(`/api/tasks/${t.id}`))));
}
async function show(task) {
  current=task;
  const area=$("#result");area.hidden=false;area.replaceChildren(node("h2","Your mock appointment task"),node("span",task.status),node("p",task.payload.reply));
  if(task.status==="CLARIFICATION_REQUIRED") area.append(node("p","Add the missing city/date above. Your next message continues this task."));
  if(["PLANNED","APPROVAL_PENDING"].includes(task.status)) for(const slot of task.payload.slots||[]) {
    area.append(button(`Review ${slot.clinic} · ${slot.city} · ${slot.starts_at} · ₹0 (MOCK)`,async()=>show(await api(`/api/tasks/${task.id}/preview`,{slot_id:slot.id,version:task.version})),"slot secondary"));
  }
  if(task.status==="APPROVAL_PENDING") {
    area.append(node("h3","Review the exact mock booking"));
    const preview=task.payload.preview, recap=node("dl");
    for(const [label,value] of [["Clinic",preview.clinic],["Service","Dental cleaning · mock only"],["City",preview.city],["Exact date and time",`${preview.starts_at} · Asia/Kolkata`],["Total","₹0 · no payment"],["Conditions",preview.cancellation_terms]]) recap.append(node("dt",label),node("dd",value));
    area.append(recap);
    const a=task.payload.approval;
    if(a.token) for(const [value,label] of [["approve","Approve MOCK booking"],["edit","Change selection"],["reject","Reject booking"]]) area.append(button(label,async()=>show(await api(`/api/approvals/${a.id}/decision`,{decision:value,token:a.token,version:task.version}))));
    else area.append(node("p","After reload, select a slot above for a fresh preview and one-time approval token."));
  }
  if(task.status==="RECONCILIATION_REQUIRED") area.append(button("Reconcile saved mock operation",async()=>show(await api(`/api/tasks/${task.id}/reconcile`,{version:task.version}))));
  if(["CLARIFICATION_REQUIRED","PLANNED","APPROVAL_PENDING","REQUIRES_USER_ACTION"].includes(task.status)) area.append(button("Cancel before commitment",async()=>show(await api(`/api/tasks/${task.id}/cancel`,{version:task.version}))));
  if(task.payload.receipt) area.append(node("pre",JSON.stringify(task.payload.receipt,null,2)),node("p","A reminder intent is durable. No background notification or real appointment was created."));
  const details=node("details"), summary=node("summary","Task plan and pinned provider roles");details.append(summary,node("pre",JSON.stringify({plan:task.payload.plan,profiles:task.profiles},null,2)));area.append(details);
  await history();area.focus();
}
async function enter(session) {csrf=session.csrf;$("#session-panel").hidden=true;$("#workspace").hidden=false;await history();$("#profiles").textContent=JSON.stringify((await api("/api/provider-connections")).profiles,null,2);}
$("#start").addEventListener("click",()=>run(async()=>enter(await api("/api/session",{consent_mock_data:true,locale:$("#locale").value}))));
$("#message-form").addEventListener("submit",e=>{e.preventDefault();run(async()=>show(await api("/api/chat/messages",{external_id:crypto.randomUUID(),text:$("#message").value,locale:$("#locale").value,...(current?.status==="CLARIFICATION_REQUIRED"?{conversation_id:current.conversation_id}:{})})));});
$("#voice").addEventListener("click",()=>run(async()=>{const locale=$("#locale").value,fixture=await api(`/api/fixtures/${locale}`);await show(await api("/api/chat/messages",{external_id:crypto.randomUUID(),audio_base64:fixture.audio_base64,mime:fixture.mime,locale}));}));
$("#refresh").addEventListener("click",()=>run(history));
api("/api/session").then(s=>{if(s.active) return enter(s);}).catch(e=>{$("#status").textContent=e.message;});
