// App principal: carrega CSVs, renderiza cards, permite adicionar itens e salvar (download ou GitHub API)
categoria: document.getElementById('newCategoria').value.trim(),
nota: document.getElementById('newNota').value.trim(),
status: document.getElementById('newStatus').value.trim(),
ano: document.getElementById('newAno').value.trim(),
source: 'local'
};
items.push(item);
// salvar no localStorage
const saved = JSON.parse(localStorage.getItem('rpg_items')||'[]');
saved.push(item);
localStorage.setItem('rpg_items', JSON.stringify(saved));


closeModal();
populateCategoryFilter();
renderCards(items);
}


// Converter items em CSV (header: titulo,categoria,nota,status,ano)
function itemsToCSV(arr){
const header = ['titulo','categoria','nota','status','ano'];
const lines = [header.join(',')];
arr.forEach(i=>{
const vals = header.map(h=>`"${String(i[h]||'').replace(/"/g,'""')}"`);
lines.push(vals.join(','));
});
return lines.join('
');
}


// Baixar CSV gerado localmente
function downloadCurrentCSV(){
const csv = itemsToCSV(items);
const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'biblioteca_export.csv';
document.body.appendChild(a);
a.click();
a.remove();
}


// GitHub API: sobrescrever arquivo no repo
async function saveCSVtoGithub({owner,repo,path,token}){
// pega o sha do arquivo (se existir)
try{
const urlGet = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;
const resp = await fetch(urlGet, { headers: { Authorization: `token ${token}` } });
let sha = null;
if(resp.ok){
const json = await resp.json();
sha = json.sha;
}


const content = itemsToCSV(items);
const b64 = btoa(unescape(encodeURIComponent(content)));


const body = {
message: 'Atualizando CSV via Painel RPG',