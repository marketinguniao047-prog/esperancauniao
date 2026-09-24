const defaultSellers=[
{id:1,name:'Vendedor PB',region:'PB',phone:'(83) 99999-0001',lat:-7.2306,lng:-35.8811},
{id:2,name:'Vendedor RN',region:'RN',phone:'(84) 99999-0002',lat:-5.7945,lng:-35.2110},
{id:3,name:'Vendedor PE',region:'PE',phone:'(81) 99999-0003',lat:-8.0476,lng:-34.8770},
{id:4,name:'Vendedor CE',region:'CE',phone:'(85) 99999-0004',lat:-3.7319,lng:-38.5267},
];
let sellers=JSON.parse(localStorage.getItem('uniaoSellers')||'null')||defaultSellers;
const map=L.map('map').setView([-6.2,-36.0],6);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'}).addTo(map);let markers={};
const internal=[{name:'Atendimento 01',phone:'(00) 00000-0001'},{name:'Atendimento 02',phone:'(00) 00000-0002'},{name:'Atendimento 03',phone:'(00) 00000-0003'}];
function initials(n){return n.split(' ').map(x=>x[0]).slice(0,2).join('').toUpperCase()}
function renderInternal(){document.querySelector('#internal-list').innerHTML=internal.map(p=>`<div class="person"><div class="avatar">${initials(p.name)}</div><div><h4>${p.name}</h4><p>${p.phone}</p></div></div>`).join('')}
function renderSellers(){Object.values(markers).forEach(m=>m.remove());markers={};const filter=document.querySelector('#regionFilter').value;const visible=sellers.filter(s=>filter==='all'||s.region===filter);visible.forEach(s=>{const marker=L.marker([s.lat,s.lng],{draggable:true}).addTo(map);marker.bindPopup(`<strong>${s.name}</strong><br>${s.region} • ${s.phone}<br><small>Arraste para mover</small>`);marker.on('dragend',()=>{const p=marker.getLatLng();s.lat=+p.lat.toFixed(5);s.lng=+p.lng.toFixed(5);save();renderRegional();});markers[s.id]=marker});renderRegional()}
function renderRegional(){const filter=document.querySelector('#regionFilter').value;const visible=sellers.filter(s=>filter==='all'||s.region===filter);document.querySelector('#regional-list').innerHTML=visible.map(s=>`<div class="regional-item"><strong>${s.name}</strong><span>${s.region} • ${s.phone}</span><button class="remove" data-id="${s.id}" style="margin-top:8px;border:0;background:none;color:#b23;cursor:pointer">Remover</button></div>`).join('');document.querySelectorAll('.remove').forEach(b=>b.onclick=()=>{sellers=sellers.filter(s=>s.id!==+b.dataset.id);save();renderSellers()})}
function save(){localStorage.setItem('uniaoSellers',JSON.stringify(sellers))}
renderInternal();renderSellers();document.querySelector('#regionFilter').onchange=renderSellers;document.querySelector('#resetSellers').onclick=()=>{sellers=JSON.parse(JSON.stringify(defaultSellers));save();renderSellers()};
const modal=document.querySelector('#sellerModal');document.querySelector('#addSeller').onclick=()=>modal.classList.add('open');document.querySelector('#closeModal').onclick=()=>modal.classList.remove('open');
document.querySelector('#sellerForm').onsubmit=e=>{e.preventDefault();const f=new FormData(e.target);sellers.push({id:Date.now(),name:f.get('name'),region:f.get('region'),phone:f.get('phone'),lat:+f.get('lat'),lng:+f.get('lng')});save();renderSellers();modal.classList.remove('open');e.target.reset()};
document.querySelector('.menu-toggle').onclick=()=>document.querySelector('.main-nav').classList.toggle('open');document.querySelectorAll('.main-nav a').forEach(a=>a.onclick=()=>document.querySelector('.main-nav').classList.remove('open'));
