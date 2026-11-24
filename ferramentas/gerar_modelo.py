"""Gera a VERSÃO MODELO (genérica) do sistema a partir da versão da ID Soluções.

Uso:  python3 ferramentas/gerar_modelo.py  PASTA_DE_SAIDA
Ex.:  python3 ferramentas/gerar_modelo.py ../sistema-assistencia-modelo

O que ele faz:
- tira dados da empresa, nomes da equipe, usuário administrador fixo e o banco da ID Soluções;
- faz o site ler o endereço/chave do banco de um arquivo config.js (cada loja usa o seu Supabase);
- troca o símbolo "iD" pelas iniciais da loja que instalar;
- acrescenta o assistente de instalação no primeiro acesso do administrador;
- gera o SQL de instalação com usuário/nome/senha do administrador a preencher.
Assim, toda melhoria feita na versão da loja pode ser repassada ao modelo rodando este script de novo.
"""
import sys, re, os, shutil, pathlib

R = pathlib.Path(__file__).resolve().parent.parent          # pasta do projeto da ID Soluções
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else R.parent / 'sistema-assistencia-modelo').resolve()
DOMINIO = 'loja.app'   # domínio interno dos usuários (ninguém recebe e-mail; precisa ser igual no SQL)

def troca(s, old, new, count=1, nome=''):
    n = s.count(old)
    if n != count:
        sys.exit(f'[{nome}] trecho encontrado {n}x (esperado {count}): {old[:90]!r}')
    return s.replace(old, new)

# ---------------------------------------------------------------- sistema.html
s = (R / 'fonte/sistema.html').read_text(encoding='utf-8')
S = lambda old, new, count=1: troca(s, old, new, count, 'sistema.html')

s = S('<title>ID Soluções</title>', '<title>Sistema da loja</title>')
s = S('<b id="brandLoja">ID Soluções</b>', '<b id="brandLoja">Minha loja</b>')
# dados da empresa de exemplo (só aparecem na demonstração local, nunca na versão online)
i = s.index('const LOJA_NOVA={'); j = s.index('};', i) + 2
s = s[:i] + "const LOJA_NOVA={razao:'Loja Exemplo Ltda',cnpj:'00.000.000/0001-00',ie:'',im:'',end:'Rua Exemplo, 100',bairro:'Centro',cidade:'São Paulo',uf:'SP',cep:'',tel:'',whats:'',cuf:35};" + s[j:]
i = s.index('const LOJA_V1={'); j = s.index('};', i) + 2
s = s[:i] + 'const LOJA_V1={};' + s[j:]
s = s.replace("fantasia:'ID Soluções'", "fantasia:'Loja Exemplo'")
s = s.replace("'ID Soluções':LOJA", "'Loja Exemplo':LOJA")
s = S("const n='Cleisson Fernandes'", "const n=(typeof ON!=='undefined'&&ON.perfil&&ON.perfil.nome)||'Dono'")
s = S('@idsolucoes', '@sualoja')
s = s.replace('Kaique', 'Bruno').replace('Luciana', 'Marina')   # equipe dos dados de exemplo
# símbolo: iniciais da loja no lugar do "iD"
i = s.index("const LOGO_SVG='"); j = s.index("';", i) + 2
s = s[:i] + r"""function logoIniciais(){const n=String((typeof DB!=='undefined'&&DB&&DB.loja&&DB.loja.fantasia)||(()=>{try{return localStorage.getItem(KEY+'-nome')}catch(e){return ''}})()||'Minha loja').trim();const p=n.split(/\s+/).filter(w=>w.length>2||/^[A-Z0-9]/.test(w));const ini=((p[0]||n)[0]+((p[1]||'')[0]||'')).toUpperCase();return `<svg class="logo" width="34" height="34" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#141821"/><circle cx="25.5" cy="6.5" r="2.4" fill="var(--accent)"/><text x="16" y="21.5" text-anchor="middle" font-family="Inter,system-ui,sans-serif" font-weight="700" font-size="${ini.length>1?13:15}" fill="#fff">${ini.replace(/[<&]/g,'')}</text></svg>`}
Object.defineProperty(window,'LOGO_SVG',{get:logoIniciais});""" + s[j:]
s = S("  $('#brandLoja').textContent=DB.loja.fantasia;",
      "  $('#brandLoja').textContent=DB.loja.fantasia||'Minha loja';try{localStorage.setItem(KEY+'-nome',DB.loja.fantasia||'')}catch(e){}")
s = S('const mk=$(\'.side .mark\');if(mk&&mk.dataset.logo!==(DB.loja.logo||\'\'))',
      'const mk=$(\'.side .mark\');if(mk&&mk.dataset.logo!==(DB.loja.logo||\'\')+\'|\'+DB.loja.fantasia)')
s = S("mk.dataset.logo=DB.loja.logo||'';", "mk.dataset.logo=(DB.loja.logo||'')+'|'+DB.loja.fantasia;")
for x in ['Cleisson', 'ID Soluções', 'idsolucoes', 'Kaique', 'Luciana', '57.631', '129641685', 'Holandeses', '99125']:
    if x in s: sys.exit(f'sistema.html ainda contém {x!r}')

# ---------------------------------------------------------------- online.js
o = (R / 'fonte/online.js').read_text(encoding='utf-8')
O = lambda old, new, count=1: troca(o, old, new, count, 'online.js')
i = o.index('const ONLINE={'); j = o.index('};', i) + 2
o = o[:i] + f"""const ONLINE=(()=>{{const c=window.SISTEMA_CONFIG||{{}};return {{url:String(c.supabaseUrl||'').replace(/\\/+$/,''),key:String(c.supabaseChavePublica||''),dominio:'{DOMINIO}'}}}})();""" + o[j:]
i = o.index('  D.funcionarios=['); j = o.index('];', i) + 2
o = o[:i] + "  D.funcionarios=[{id:'f0',nome:(ON.perfil&&ON.perfil.nome)||'Administrador',funcao:'Dono',dono:true,tel:'',cpf:'',pix:'',comServico:0,comVenda:0,soSemDono:false,vendaAparelho:false,ativo:true}];" + o[j:]
o = O("  return {loja:{...lojaBase,margemPadrao:lojaBase.margemPadrao??30},",
      "  ['fantasia','razao','cnpj','ie','im','end','bairro','cidade','uf','cep','tel','whats'].forEach(k=>lojaBase[k]='');lojaBase.cuf=0;\n  return {loja:{...lojaBase,margemPadrao:lojaBase.margemPadrao??30},")
o = o.replace('ao Cleisson', 'ao administrador').replace('o Cleisson', 'o administrador').replace('O Cleisson', 'O administrador')
o = O('<div><b>ID Soluções</b><small>Sistema da loja</small></div>',
      '<div><b>${esc((()=>{try{return localStorage.getItem(KEY+\'-nome\')}catch(e){return \'\'}})()||\'Sistema da loja\')}</b><small>Sistema da loja</small></div>')
o = O("  if(!window.supabase||!window.supabase.createClient){onCarregando('Sem conexão com a internet. Recarregue a página.');return}",
      "  if(!ONLINE.url||!ONLINE.key||/SEU-PROJETO/.test(ONLINE.url)||/COLE_AQUI/.test(ONLINE.key)){onCarregando('Falta configurar o arquivo config.js com o endereço e a chave pública do seu Supabase (veja o guia de instalação).');return}\n  if(!window.supabase||!window.supabase.createClient){onCarregando('Sem conexão com a internet. Recarregue a página.');return}")
o = O("  $('#login').hidden=true;onAssinar();onAgendar();",
      "  $('#login').hidden=true;onAssinar();onAgendar();\n  if(ehDono()&&!String(DB.loja.fantasia||'').trim())setTimeout(onBoasVindas,300);")
o += r"""

/* ---- primeiro acesso do administrador: dados da loja ---- */
const UFS='AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split(' ');
const CUF={RO:11,AC:12,AM:13,RR:14,PA:15,AP:16,TO:17,MA:21,PI:22,CE:23,RN:24,PB:25,PE:26,AL:27,SE:28,BA:29,MG:31,ES:32,RJ:33,SP:35,PR:41,SC:42,RS:43,MS:50,MT:51,GO:52,DF:53};
function onBoasVindas(){
  const L=DB.loja;FORM={kind:'boasvindas',d:{fantasia:L.fantasia||'',razao:L.razao||'',cnpj:L.cnpj||'',whats:L.whats||'',end:L.end||'',bairro:L.bairro||'',cidade:L.cidade||'',uf:L.uf||'',cep:L.cep||''}};
  const f=(l,k,x='',cls='')=>fld(l,`<input data-f="d.${k}" id="bv-${k}" value="${esc(FORM.d[k])}" ${x}>`,cls);
  openModal('Bem-vindo! Vamos configurar a sua loja',`<div class="sec"><p class="muted" style="margin:0">Estes dados aparecem no menu, nos comprovantes e nas mensagens aos clientes. Dá para mudar depois em Configurações.</p><div class="g2">
    ${f('Nome da loja','fantasia','placeholder="Ex.: Assistência Silva"','span2')}${f('Razão social','razao')}${f('CNPJ','cnpj','data-mask="cpf" inputmode="numeric"')}
    ${f('WhatsApp','whats','data-mask="tel" inputmode="tel"')}${f('CEP','cep')}${f('Endereço','end','placeholder="Rua, número, loja"','span2')}${f('Bairro','bairro')}${f('Cidade','cidade')}
    ${fld('UF',`<select data-f="d.uf" id="bv-uf">${optV([['','—'],...UFS.map(u=>[u,u])],FORM.d.uf)}</select>`)}
  </div></div>`,`<span class="form-err" id="bvErr"></span><button class="btn" data-act="closeModal">Depois</button><button class="btn pri" data-act="onBoasVindasOk">${ic('check')}Salvar e começar</button>`);
  setTimeout(()=>{const e=$('#bv-fantasia');if(e)e.focus()},50);
}
ACT.onBoasVindasOk=()=>{const d=FORM&&FORM.kind==='boasvindas'?FORM.d:null;if(!d)return;
  if(!String(d.fantasia||'').trim()){$('#bvErr').textContent='Informe o nome da loja.';return}
  Object.keys(d).forEach(k=>DB.loja[k]=String(d[k]||'').trim());DB.loja.cuf=CUF[DB.loja.uf]||0;save();closeModal();route();
  toast('Pronto! Agora cadastre a equipe em Funcionários e envie a logo em Configurações.')};
"""
for x in ['Cleisson', 'ID Soluções', 'idsolucoes', 'Kaique', 'Luciana', 'qmzfzolahqjwaixbirom', 'sb_publishable_']:
    if x in o: sys.exit(f'online.js ainda contém {x!r}')

# ---------------------------------------------------------------- SQL
q = (R / 'banco/instalar-do-zero.sql').read_text(encoding='utf-8')
q = q.replace('ID Soluções · Sistema da loja · BANCO DE DADOS COMPLETO', 'Sistema da loja · BANCO DE DADOS COMPLETO')
q = q.replace("--   3. No FINAL do arquivo, troque TROQUE_AQUI pela senha do administrador",
              "--   3. No FINAL do arquivo, preencha usuário, nome e senha do administrador")
q = q.replace('idsolucoes.app', DOMINIO)
i = q.index('-- 10) ADMINISTRADOR')
q = q[:q.rindex('-- -----', 0, i)] + """-- ---------------------------------------------------------------------
-- 10) ADMINISTRADOR: quem vai cuidar do sistema
-- ---------------------------------------------------------------------
-- PREENCHA as 3 linhas abaixo antes de clicar em Run:
--   usuario → uma palavra, minúscula, sem espaço nem acento (ex.: joao)
--   nome    → o nome que aparece no sistema (ex.: João Silva)
--   senha   → mínimo 6 caracteres
-- Se o usuário já existir, a senha é redefinida para esta.
-- Os demais usuários são criados DENTRO do sistema, em
-- Funcionários › Usuários do sistema › Novo usuário.
do $$
declare
  usuario text := 'TROQUE_AQUI';
  nome    text := 'TROQUE_AQUI';
  senha   text := 'TROQUE_AQUI';
begin
  if 'TROQUE_AQUI' in (usuario, nome, senha) then
    raise exception 'Preencha usuário, nome e senha do administrador (no fim do texto) antes de clicar em Run.';
  end if;
  perform public._criar_conta(usuario, nome, 'dono', 'f0', senha);
end $$;
"""
for x in ['cleisson', 'Cleisson', 'ID Soluções', 'idsolucoes']:
    if x in q: sys.exit(f'SQL ainda contém {x!r}')

# ---------------------------------------------------------------- função da IA
a = (R / 'supabase-funcao/assistente.ts').read_text(encoding='utf-8')
a = troca(a, 'Deno.env.get("SUPABASE_ANON_KEY") || "sb_publishable_wTkCcEQbWoOIZO4sFaiOxg_j56moawA", // chave pública do projeto',
          'Deno.env.get("SUPABASE_ANON_KEY") || req.headers.get("apikey") || "", // chave pública do projeto', 1, 'assistente.ts')
a = a.replace('// ID Soluções · função "assistente"', '// Sistema da loja · função "assistente"')
if 'sb_publishable_' in a or 'ID Soluções' in a: sys.exit('assistente.ts ainda tem dados da ID Soluções')

# ---------------------------------------------------------------- montador do site (modelo)
m = (R / 'ferramentas/montar_site.py').read_text(encoding='utf-8')
m = troca(m, 'rep("<title>ID Soluções</title>","<title>ID Soluções · Sistema</title>")', 'rep("<title>Sistema da loja</title>","<title>Sistema da loja</title>")', 1, 'montar_site.py')
m = troca(m, '<script src="{SB_URL}"></script>\\n', '<script src="config.js"></script>\\n<script src="{SB_URL}"></script>\\n', 1, 'montar_site.py')
m = m.replace('content="ID Soluções"', 'content="Sistema da loja"')
m = troca(m, "with zipfile.ZipFile(D+'site-pronto/id-solucoes-site.zip','w',zipfile.ZIP_DEFLATED) as z: z.write(D+'site-pronto/index.html','index.html')\nprint('site pronto:',D+'site-pronto/id-solucoes-site.zip')",
          "import shutil\nif not os.path.exists(D+'site-pronto/config.js'): shutil.copy(D+'fonte/config.exemplo.js',D+'site-pronto/config.js')\nwith zipfile.ZipFile(D+'site-pronto/site.zip','w',zipfile.ZIP_DEFLATED) as z:\n    z.write(D+'site-pronto/index.html','index.html'); z.write(D+'site-pronto/config.js','config.js')\nprint('site pronto:',D+'site-pronto/site.zip')", 1, 'montar_site.py')

# ---------------------------------------------------------------- grava tudo
for d in ['fonte', 'banco', 'supabase-funcao', 'ferramentas', 'site-pronto', 'docs']:
    (OUT / d).mkdir(parents=True, exist_ok=True)
(OUT / 'fonte/sistema.html').write_text(s, encoding='utf-8')
(OUT / 'fonte/online.js').write_text(o, encoding='utf-8')
shutil.copy(R / 'fonte/icone.b64', OUT / 'fonte/icone.b64')
(OUT / 'fonte/config.exemplo.js').write_text("""// CONFIGURAÇÃO DO SEU SISTEMA
// Preencha com os dados do SEU projeto no Supabase (Project Settings › Data API e › API Keys).
// Use SOMENTE a chave "Publishable" (começa com sb_publishable_). NUNCA a "Secret".
window.SISTEMA_CONFIG = {
  supabaseUrl: 'https://SEU-PROJETO.supabase.co',
  supabaseChavePublica: 'sb_publishable_COLE_AQUI'
};
""", encoding='utf-8')
(OUT / 'banco/instalar-do-zero.sql').write_text(q, encoding='utf-8')
(OUT / 'supabase-funcao/assistente.ts').write_text(a, encoding='utf-8')
(OUT / 'ferramentas/montar_site.py').write_text(m, encoding='utf-8')
for f in ['mock_supabase.js', 'mock_server.js']:
    t = (R / 'ferramentas' / f).read_text(encoding='utf-8').replace('idsolucoes.app', DOMINIO)
    t = t.replace("{usuario:'cleisson',nome:'Cleisson Fernandes',", "{usuario:'admin',nome:'Administrador Teste',").replace("'cleisson@", "'admin@")
    (OUT / 'ferramentas' / f).write_text(t, encoding='utf-8')
# guias e teste de instalação
for f in ['README.md', 'INSTALAR.md']:
    shutil.copy(R / 'modelo' / f, OUT / f)
shutil.copy(R / 'modelo/teste_instalacao.js', OUT / 'ferramentas/teste_instalacao.js')
mapa = (R / 'docs/2-mapa-do-codigo.md').read_text(encoding='utf-8').replace('# 2. Mapa do código', '# Mapa do código')
mapa = mapa.replace('fonte/sistema.html   → o sistema inteiro', 'fonte/sistema.html   → o sistema inteiro').replace('fonte/online.js      → a camada online', 'fonte/config.exemplo.js → modelo do config.js (endereço e chave do Supabase de cada loja)\nfonte/online.js      → a camada online')
mapa = mapa.replace("| `ONLINE` | endereço e chave pública do Supabase; domínio interno dos usuários |", "| `ONLINE` | lê o endereço e a chave pública do Supabase do `config.js`; domínio interno dos usuários |")
mapa += "\n| `onBoasVindas` | (no fim do `online.js`) primeiro acesso do administrador: dados da loja |\n"
(OUT / 'docs/mapa-do-codigo.md').write_text(mapa, encoding='utf-8')
telas = (R / 'docs/3-telas.md').read_text(encoding='utf-8').replace('# 3. Telas do sistema', '# Telas do sistema')
telas = telas.replace('**A** = administrador (Cleisson) · **T** = técnico (Kaique) · **V** = vendedora (Luciana).', '**A** = administrador · **T** = técnico · **V** = vendedor(a).')
telas = telas.replace("| **Entrar** | todos |", "| **Bem-vindo (primeiro acesso)** | A | Nome da loja, razão social, CNPJ, WhatsApp e endereço. |\n| **Entrar** | todos |")
(OUT / 'docs/telas.md').write_text(telas, encoding='utf-8')
(OUT / '.gitignore').write_text('.DS_Store\n*.tmp\n', encoding='utf-8')
for f in OUT.rglob('*'):
    if f.is_file() and f.suffix in ('.md', '.js', '.py', '.sql', '.ts', '.html') and f.name != 'teste_instalacao.js':  # o teste procura esses nomes de propósito
        t = f.read_text(encoding='utf-8')
        for x in ['Cleisson', 'cleisson', 'ID Soluções', 'idsolucoes', 'Kaique', 'Luciana', 'qmzfzolahqjwaixbirom', '57.631', 'Holandeses']:
            if x in t: sys.exit(f'{f} ainda contém {x!r}')
print('modelo gerado em', OUT)
