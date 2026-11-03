// Paste ONCE per page load with javascript_tool (Easy Apply modal must be open). Then call:
//   __text()            -> current modal page text (questions)
//   __q()               -> inputs with ids: [{q, kind, id, val, opts}] ; radios: fieldset ids in order (Yes first, No second)
//   __set(id, value)    -> set text/textarea/select value React-safely
//   __radio(id)         -> click a radio input by id
//   __next()            -> click Next/Review; returns 'AT SUBMIT' when only Submit is left
//   __submit()          -> click "Submit application"
//   __email('you@example.com') -> force the email select to your application address (TODO: use the email in profile/qa_bank.md)
window.__modal=()=>{const btn=[...document.querySelectorAll('button')].find(b=>/^(Next|Review|Submit application)$/i.test(b.innerText.trim())); let d=btn; while(d&&!(d.innerText||'').startsWith('Apply to'))d=d.parentElement; return d};
window.__text=()=>{const m=window.__modal(); return m?m.innerText.replace(/\n{2,}/g,'\n').slice(0,3000):'NO MODAL: '+document.body.innerText.slice(0,400)};
window.__q=()=>{const root=window.__modal(); const out=[]; root.querySelectorAll('fieldset').forEach(fs=>{out.push({kind:'radio',opts:[...fs.querySelectorAll('input')].map(i=>({id:i.id,label:(i.parentElement?.innerText||'').trim(),on:i.checked}))})}); root.querySelectorAll('input[type=text],input[type=number],input[type=tel],input[type=email],textarea,select').forEach(e=>{if(e.closest('fieldset'))return; const lab=(document.querySelector(`label[for="${CSS.escape(e.id)}"]`)?.innerText||e.getAttribute('aria-label')||'').trim().split('\n')[0]; const o={q:lab,kind:e.tagName.toLowerCase(),id:e.id,val:e.value}; if(e.tagName==='SELECT')o.opts=[...e.options].map(x=>x.text.trim()).slice(0,25); out.push(o)}); return JSON.stringify(out)};
window.__set=(id,v)=>{const e=document.getElementById(id); const proto=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:(e.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(proto,'value').set.call(e,v); ['input','change','blur'].forEach(t=>e.dispatchEvent(new Event(t,{bubbles:true}))); return e.value.slice(0,40)};
window.__radio=(id)=>{const e=document.getElementById(id); (document.querySelector(`label[for="${CSS.escape(id)}"]`)||e).click(); return e.checked};
window.__next=()=>{const m=window.__modal(); if(!m) return 'no modal'; const b=[...m.querySelectorAll('button')].reverse().find(b=>/^(Next|Review|Submit application)$/i.test(b.innerText.trim())); if(!b) return 'no next'; const t=b.innerText.trim(); if(/Submit/i.test(t)) return 'AT SUBMIT'; b.click(); return 'clicked '+t};
window.__submit=()=>{const m=window.__modal(); const b=[...m.querySelectorAll('button')].find(b=>/^Submit application$/i.test(b.innerText.trim())); if(!b) return 'no submit'; b.click(); return 'submitted'};
window.__email=(addr)=>{if(!addr) return 'pass your email: __email("you@example.com")'; const s=[...window.__modal().querySelectorAll('select')].find(s=>[...s.options].some(o=>o.text.includes(addr))); if(!s) return 'no email select'; return window.__set(s.id,addr)};
'helpers ready';
