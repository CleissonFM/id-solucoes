"""Gera a VERSÃO LOCAL (grátis, sem banco de dados) a partir do modelo genérico.

Uso:  python3 ferramentas/gerar_modelo.py ../sistema-assistencia-modelo     (primeiro o modelo)
      python3 ferramentas/gerar_local.py  ../sistema-assistencia-modelo     (depois esta)

Como funciona a versão local:
- a pessoa abre o link, preenche o nome dela e da loja e já usa. Sem login, sem Supabase, sem config.js;
- tudo fica guardado NO PRÓPRIO APARELHO (IndexedDB do navegador). Nada vai para servidor nenhum;
- dá para instalar como aplicativo (celular e computador) e funciona sem internet;
- Configurações › Cópia de segurança: baixar e importar o arquivo com todos os dados (para trocar de aparelho);
- o assistente de IA fica escondido (precisa de servidor).
Saída: PASTA/versao-local/  (index.html, manifest.webmanifest, sw.js, icone.png) + versao-local.zip
"""
import sys, re, os, pathlib, base64, zipfile, io

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent.parent / 'sistema-assistencia-modelo').resolve()
R = pathlib.Path(__file__).resolve().parent.parent
s = (OUT / 'fonte/sistema.html').read_text(encoding='utf-8')

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: sys.exit(f'trecho encontrado {n}x (esperado {count}): {old[:100]!r}')
    s = s.replace(old, new)

css = '''
/* Versão local */
[data-top="ia"],.nav-ai,.ai-card,.ai-ask,#ai{display:none!important}
.loc-aviso{display:flex;gap:10px;align-items:flex-start;background:var(--soft,#EEF2FF);border-radius:12px;padding:12px 14px;font-size:13px;line-height:1.45;color:var(--fg)}
.loc-aviso b{font-weight:600}
'''
rep('/* Adaptação à largura disponível */', css + '\n/* Adaptação à largura disponível */')
rep('<title>Sistema da loja</title>', '<title>Sistema da Assistência</title>')
rep('placeholder="Buscar ou perguntar à IA"', 'placeholder="Buscar OS, cliente, IMEI…"')
rep('Na versão online, a emissão real será feita por um emissor integrado (via API) usando o certificado da loja. Enquanto isso, tudo funciona em simulação para treinar a equipe.',
    'Aqui a nota fiscal é só uma simulação, para organizar e treinar a equipe. Para emitir nota de verdade, use o emissor da sua contabilidade ou da prefeitura.')
rep("function route(){\n", "function route(){if(!DB||!LAY)return;\n")
rep("function save(){try{localStorage.setItem(KEY,JSON.stringify(DB))}catch(e){}}",
    "function save(){if(!LOC.pronto)return;clearTimeout(LOC.timer);LOC.timer=setTimeout(locGravar,250)}")

local = r'''
/* ========== Versão local: tudo fica guardado neste aparelho (IndexedDB) ========== */
var LOC={db:null,timer:null,pronto:false};
function locAbrir(){return new Promise((ok,no)=>{const r=indexedDB.open('sistema-assistencia',1);r.onupgradeneeded=()=>r.result.createObjectStore('dados');r.onsuccess=()=>ok(r.result);r.onerror=()=>no(r.error)})}
function locLer(){return new Promise((ok,no)=>{const q=LOC.db.transaction('dados').objectStore('dados').get('principal');q.onsuccess=()=>ok(q.result);q.onerror=()=>no(q.error)})}
function locGravar(){LOC.timer=null;if(!LOC.db||!DB)return Promise.resolve();const json=JSON.stringify(DB);
  return new Promise(ok=>{const tx=LOC.db.transaction('dados','readwrite');tx.objectStore('dados').put(json,'principal');
    tx.oncomplete=()=>ok(true);tx.onerror=tx.onabort=()=>{toast('Não foi possível salvar neste aparelho. Libere espaço e tente de novo.');ok(false)}})}
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&LOC.timer){clearTimeout(LOC.timer);locGravar()}});
window.addEventListener('pagehide',()=>{if(LOC.timer){clearTimeout(LOC.timer);locGravar()}});
// banco em branco: mesma estrutura dos dados de exemplo, sem nenhum registro
function locVazio(nome){const keep=DB;seed();const D=DB;DB=keep;
  Object.keys(D).forEach(k=>{if(Array.isArray(D[k]))D[k]=[]});D.comPagas={};
  Object.keys(D.loja).forEach(k=>{if(typeof D.loja[k]==='string'&&!['regime','horario','termos'].includes(k))D.loja[k]=''});D.loja.cuf=0;D.loja.logo='';
  D.funcionarios=[{id:'f0',nome:nome||'Dono',funcao:'Dono',dono:true,tel:'',cpf:'',pix:'',comServico:0,comVenda:0,soSemDono:false,vendaAparelho:false,ativo:true}];
  D.seq={os:1,venda:1,gasto:0,nf:{'NFC-e':1,'NF-e':1,'NFS-e':1}};
  const k2=DB;DB=D;try{D.metas=metasPadrao()}catch(e){D.metas=[]}DB=k2;return D}
// arquivos: download de verdade (cópia e planilha)
baixarArquivo=async(nome,txt)=>{const tipo=nome.endsWith('.json')?'application/json':'text/csv;charset=utf-8';
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([nome.endsWith('.csv')?'﻿'+txt:txt],{type:tipo}));a.download=nome;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},1500);
  if(nome.endsWith('.json')){try{localStorage.setItem('sa-ultima-copia',String(Date.now()))}catch(e){}toast('Cópia baixada. Guarde no Google Drive ou mande para o seu WhatsApp.')}else toast('Planilha baixada')};
ACT.backupJSON=()=>baixarArquivo(`copia-sistema-${ymd(new Date())}.json`,JSON.stringify(DB));
// Configurações: cópia de segurança, importar e apagar
const _vConfigLocal=vConfig;
vConfig=()=>_vConfigLocal().replace(/<section class="sec"><div class="sec-h"><h3>Dados do protótipo<\/h3>[\s\S]*?<\/section>/,`<section class="sec"><div class="sec-h"><h3>Cópia de segurança</h3><small>Seus dados ficam só neste aparelho</small></div>
  <div class="loc-aviso">${ic('alert',18)}<div>Tudo o que você cadastra fica guardado <b>neste aparelho, neste navegador</b>. Nada vai para a internet. Se você trocar de aparelho, limpar os dados do navegador ou perder o aparelho, os dados vão junto. <b>Baixe uma cópia toda semana</b> e guarde no Google Drive ou no seu WhatsApp.</div></div>
  <div class="tgs"><button class="btn pri" data-act="backupJSON">${ic('doc',16)}Baixar cópia dos dados</button><label class="btn">${ic('swap',16)}Importar cópia<input type="file" accept=".json,application/json" id="locImport" hidden></label></div>
  <p class="ai-note" style="margin:0">Para levar o sistema para outro aparelho: baixe a cópia aqui e use "Importar cópia" no aparelho novo.</p>
  <div class="tgs"><button class="btn danger" data-act="locApagar">Apagar todos os dados</button></div></section>
  <section class="sec"><div class="sec-h"><h3>Sobre</h3></div><p class="muted" style="margin:0">Sistema gratuito para assistência técnica, criado por Cleisson Fernandes · ID Soluções (São Luís - MA).</p></section>`);
document.addEventListener('change',async e=>{if(e.target.id!=='locImport')return;const f=e.target.files[0];e.target.value='';if(!f)return;
  try{const d=JSON.parse(await f.text());if(!d||!Array.isArray(d.os)||!d.loja)throw new Error('o arquivo não é uma cópia deste sistema');LOC.importar=d;
    openModal('Importar cópia',`<p style="margin:0">Substituir <b>todos</b> os dados deste aparelho pelos do arquivo <b>${esc(f.name)}</b>?</p><p class="muted">${d.os.length} OS · ${(d.vendas||[]).length} vendas · ${(d.clientes||[]).length} clientes · ${(d.iphones||[]).length} aparelhos</p>`,`<button class="btn" data-act="closeModal">Cancelar</button><button class="btn pri" data-act="locImportOk">Substituir</button>`,true)}
  catch(x){toast('Não deu para importar: '+x.message)}});
ACT.locImportOk=async()=>{const d=LOC.importar;if(!d)return;const base=locVazio();DB={...base,...d,loja:{...base.loja,...d.loja}};try{migrarLoja();migrar2();migrar3();migrarDono()}catch(x){}
  LOC.importar=null;closeModal();CART=novoCarrinho();await locGravar();route();toast('Cópia importada')};
ACT.locApagar=b=>{if(!b.dataset.armed){b.dataset.armed='1';b.textContent='Tem certeza? Clique de novo para apagar TUDO';setTimeout(()=>{if(b.isConnected){delete b.dataset.armed;b.textContent='Apagar todos os dados'}},5000);return}
  DB=locVazio();CART=novoCarrinho();locGravar();location.hash='painel';route();setTimeout(locBoasVindas,200)};
ACT.reset=ACT.locApagar;
// primeiro acesso: só o nome da pessoa e da loja
const UFS='AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split(' ');
const CUF={RO:11,AC:12,AM:13,RR:14,PA:15,AP:16,TO:17,MA:21,PI:22,CE:23,RN:24,PB:25,PE:26,AL:27,SE:28,BA:29,MG:31,ES:32,RJ:33,SP:35,PR:41,SC:42,RS:43,MS:50,MT:51,GO:52,DF:53};
function locBoasVindas(){const L=DB.loja,dono=(DB.funcionarios||[]).find(f=>f.dono)||{};
  FORM={kind:'boasvindas',d:{nome:dono.nome&&dono.nome!=='Dono'?dono.nome:'',fantasia:L.fantasia||'',whats:L.whats||'',cidade:L.cidade||'',uf:L.uf||''}};
  const f=(l,k,x='',cls='')=>fld(l,`<input data-f="d.${k}" id="bv-${k}" value="${esc(FORM.d[k])}" ${x}>`,cls);
  openModal('Bem-vindo! Vamos começar',`<div class="sec"><p class="muted" style="margin:0">Leva 1 minuto. O resto (CNPJ, endereço, logo, equipe) você completa depois em Configurações.</p><div class="g2">
    ${f('Seu nome','nome','placeholder="Ex.: João Silva" autocomplete="name"','span2')}${f('Nome da loja','fantasia','placeholder="Ex.: Assistência Silva"','span2')}
    ${f('WhatsApp da loja','whats','data-mask="tel" inputmode="tel"')}${f('Cidade','cidade')}
    ${fld('UF',`<select data-f="d.uf" id="bv-uf">${optV([['','—'],...UFS.map(u=>[u,u])],FORM.d.uf)}</select>`)}</div>
    <div class="loc-aviso">${ic('lock',18)}<div>Seus dados ficam <b>só neste aparelho</b>, ninguém mais vê. Faça uma cópia de segurança toda semana em Configurações.</div></div>
    <p class="ai-note" style="margin:0">Dica: instale como aplicativo. No Android/Chrome: menu ⋮ › <b>Instalar app</b>. No iPhone/Safari: <b>Compartilhar › Adicionar à Tela de Início</b>.</p></div>`,
    `<span class="form-err" id="bvErr"></span><button class="btn pri" data-act="locBoasVindasOk">${ic('check')}Começar a usar</button>`,true);
  setTimeout(()=>{const e=$('#bv-nome');if(e)e.focus()},50)}
ACT.locBoasVindasOk=()=>{const d=FORM&&FORM.kind==='boasvindas'?FORM.d:null;if(!d)return;
  if(!String(d.nome||'').trim()){$('#bvErr').textContent='Informe o seu nome.';return}
  if(!String(d.fantasia||'').trim()){$('#bvErr').textContent='Informe o nome da loja.';return}
  const dono=DB.funcionarios.find(f=>f.dono);if(dono)dono.nome=String(d.nome).trim();
  ['fantasia','whats','cidade','uf'].forEach(k=>DB.loja[k]=String(d[k]||'').trim());DB.loja.cuf=CUF[DB.loja.uf]||0;
  save();closeModal();route();toast('Pronto! Comece pela sua primeira OS no botão "Nova OS".')};
// lembrete semanal de cópia
function locLembrarCopia(){let u=0;try{u=+localStorage.getItem('sa-ultima-copia')||0}catch(e){}
  const tem=(DB.os||[]).length+(DB.vendas||[]).length+(DB.clientes||[]).length;if(tem>=5&&Date.now()-u>7*864e5)setTimeout(()=>toast('Lembrete: baixe a cópia de segurança em Configurações.'),1500)}
/* ---- início ---- */
(async()=>{let s=null;
  try{LOC.db=await locAbrir();s=await locLer()}catch(e){setTimeout(()=>toast('Este navegador não deixa guardar dados. Use o Chrome ou o Safari, fora da aba anônima.'),800)}
  if(s){try{DB=JSON.parse(s);migrarLoja();migrar2();migrar3();migrarDono()}catch(e){DB=locVazio()}}else DB=locVazio();
  LOC.pronto=true;if(navigator.storage&&navigator.storage.persist)navigator.storage.persist().catch(()=>{});
  CART=novoCarrinho();LAY=loadLay();$('#ai').innerHTML=aiShellHTML();$('#pz').innerHTML=pzShellHTML();applyLayout();route();
  if(!s)locGravar();
  if(!String(DB.loja.fantasia||'').trim())setTimeout(locBoasVindas,300);else locLembrarCopia();
  if('serviceWorker' in navigator&&/^https:|^http:\/\/localhost/.test(location.href))navigator.serviceWorker.register('sw.js').catch(()=>{});
})();
'''
init = "load();CART=novoCarrinho();LAY=loadLay();$('#ai').innerHTML=aiShellHTML();$('#pz').innerHTML=pzShellHTML();applyLayout();route();"
rep(init, local)
for x in ['Kaique', 'Luciana', 'qmzfzolahqjwaixbirom', 'sb_publishable_', 'supabase']:
    if x in s: sys.exit(f'versão local ainda contém {x!r}')

D = OUT / 'versao-local'; D.mkdir(parents=True, exist_ok=True)
ICON = (OUT / 'fonte/icone.b64').read_text().strip()
png = base64.b64decode(ICON)
try:
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    for n in (192, 512):
        im.resize((n, n), Image.LANCZOS).save(D / f'icone-{n}.png')
except Exception:
    for n in (192, 512): (D / f'icone-{n}.png').write_bytes(png)
head = ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="description" content="Sistema gratuito para assistência técnica: ordens de serviço, aparelhos, vendas, estoque e clientes. Os dados ficam no seu aparelho.">'
        '<meta name="theme-color" content="#141821"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-title" content="Assistência"><link rel="manifest" href="manifest.webmanifest">'
        '<link rel="icon" type="image/png" href="icone-192.png"><link rel="apple-touch-icon" href="icone-192.png"></head><body>\n')
(D / 'index.html').write_text(head + s + '\n</body></html>\n', encoding='utf-8')
(D / 'manifest.webmanifest').write_text('''{
  "name": "Sistema da Assistência",
  "short_name": "Assistência",
  "description": "Ordens de serviço, aparelhos, vendas e estoque. Os dados ficam no seu aparelho.",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#F4F6FA",
  "theme_color": "#141821",
  "icons": [
    {"src": "icone-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ]
}
''', encoding='utf-8')
(D / 'sw.js').write_text('''// Funciona sem internet: guarda o sistema no aparelho e busca a versão nova quando houver internet.
const CACHE = 'sistema-assistencia-v1';
const ARQS = ['./', 'index.html', 'manifest.webmanifest', 'icone-192.png', 'icone-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARQS))); self.skipWaiting(); });
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  e.respondWith(fetch(r).then(resp => { const c = resp.clone(); caches.open(CACHE).then(k => k.put(r, c)); return resp; })
    .catch(() => caches.match(r, { ignoreSearch: true }).then(x => x || caches.match('index.html'))));
});
''', encoding='utf-8')
with zipfile.ZipFile(OUT / 'versao-local.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in ['index.html', 'manifest.webmanifest', 'sw.js', 'icone-192.png', 'icone-512.png']:
        z.write(D / f, f)
print('versão local gerada em', D, '· zip:', OUT / 'versao-local.zip')
