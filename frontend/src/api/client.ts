const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1';
export async function api(path:string,options:RequestInit={}){const r=await fetch(BASE+path,{headers:{'Content-Type':'application/json',...(options.headers||{})},...options});if(!r.ok){let m=`Request failed (${r.status})`;try{m=(await r.json()).error?.message||m}catch{}throw new Error(m)}if(r.status===204)return null;return r.json()}
export {BASE};
