# Sistema ID Soluções — guia do projeto

Sistema de gestão da assistência técnica ID Soluções: ordens de serviço, vendas e balcão, estoque de aparelhos e acessórios, clientes, CRM, gastos com comprovantes, comissões, metas, notas fiscais (simulação) e assistente de IA. Login por usuário e senha, banco único na nuvem e tempo real.

## Guias
| Guia | Para quê |
|---|---|
| [docs/1-criar-do-zero.md](docs/1-criar-do-zero.md) | Montar o sistema do zero: banco, login, site no ar, equipe e IA, passo a passo |
| [docs/2-mapa-do-codigo.md](docs/2-mapa-do-codigo.md) | Cada parte do código, na ordem, e o que faz |
| [docs/3-telas.md](docs/3-telas.md) | Cada tela do sistema e quem vê |
| [banco/instalar-do-zero.sql](banco/instalar-do-zero.sql) | Banco de dados completo, comentado |

## Pastas
```
fonte/            código-fonte (sistema.html + online.js)
banco/            SQL do Supabase (instalar-do-zero.sql = tudo; 1- e 2- = histórico do que já foi rodado)
supabase-funcao/  função do Assistente de IA
ferramentas/      montador do site e Supabase simulado para testes
site-pronto/      site montado (index.html) e o .zip que vai para a Cloudflare
docs/             guias
```


> **Para o Claude numa conversa nova:** este pacote é o sistema de gestão da assistência técnica ID Soluções, construído com o Cleisson. Leia este arquivo inteiro antes de mexer em qualquer coisa. As decisões abaixo já foram tomadas com o dono; não pergunte de novo o que está aqui. Faça as alterações em `fonte/`, gere o site com `python3 ferramentas/montar_site.py` e entregue o `.zip` de `site-pronto/` com o passo a passo da Cloudflare. Fale sempre em português simples, um passo de cada vez, com links diretos.

Última atualização: 24/11/2026.

---

## 1. Onde fica cada coisa

| O quê | Onde |
|---|---|
| **Sistema no ar (uso da loja)** | https://dawn-leaf-c6fb.cleissonf-moreira.workers.dev |
| Hospedagem do site | Cloudflare › Workers & Pages › **dawn-leaf-c6fb** (atualizar: **New deployment** + enviar o zip) |
| Banco de dados e login | Supabase, projeto **id-solucoes** (id `qmzfzolahqjwaixbirom`, região us-east-1, plano Free) |
| Endereço do Supabase | `https://qmzfzolahqjwaixbirom.supabase.co` |
| Chave pública do Supabase | `sb_publishable_wTkCcEQbWoOIZO4sFaiOxg_j56moawA` (pública por natureza; já está no site) |
| SQL Editor | https://supabase.com/dashboard/project/qmzfzolahqjwaixbirom/sql/new |
| Função da IA | Supabase › Edge Functions › **assistente** (verificação de JWT desligada; a função confere o login sozinha) |
| Chave da IA | Segredo `ANTHROPIC_API_KEY` no Supabase (Edge Functions › Secrets). **Nunca** pedir nem colocar no código |
| Conta da IA | Claude Console (platform.claude.com), crédito pré-pago, recarga automática desligada |
| Versão de demonstração (dados de exemplo) | https://claude.ai/artifact/Ei6qyFDkgNEAjNthk5efYZ |

Contas: GitHub (o Cleisson entrou no Supabase com o GitHub), Cloudflare, Supabase e Claude Console são todas do Cleisson. Nenhuma senha está neste pacote.

## 2. A empresa

- **Nome:** ID Soluções · **Razão social:** ID Soluções Inteligentes Ltda
- **CNPJ:** 57.631.605/0001-06 · **Inscrição estadual (MA):** 129641685 · porte ME (ex-MEI, transformada em Ltda em 2026)
- **Endereço registrado (CNPJ/SEFAZ):** Av. dos Holandeses, 1 – Loja 02, Ponta d'Areia, São Luís/MA, CEP 65077-357
- **WhatsApp:** (98) 99125-2053
- **Responsável administrativo / administrador do sistema:** Cleisson Fernandes (usuário `cleisson`)
- Kaique é sócio no contrato social, mas **trabalha como técnico** e é tratado como técnico no sistema.

Pendências da empresa: (1) confirmar se a loja funciona na Loja 02 do CNPJ ou na Loja 4 do Rio Poty Hotel (se mudou, atualizar Receita/SEFAZ antes de emitir nota real); (2) regime tributário deixado como **Simples Nacional**, a confirmar com o contador.

## 3. Pessoas, papéis e o que cada um vê

| Usuário | Papel no sistema | Vê / faz |
|---|---|---|
| `cleisson` | **dono** (único administrador) | Tudo. Cria, troca senha, bloqueia e apaga usuários (Funcionários › Usuários do sistema). Configurações, logo, dados da empresa |
| `kaique` | **técnico** | Painel, Assistente IA, Ordens de serviço, Aparelhos na loja, Aparelhos à venda, Acessórios, Clientes, Comissões (só as dele), Metas |
| `luciana` | **vendedor** | Painel, Assistente IA, Ordens de serviço (abre, acompanha, avisa, entrega e recebe; só não executa), Aparelhos na loja, Vendas, Relacionamento (CRM), Gastos, Aparelhos à venda, Acessórios, Clientes, Comissões (só as dela), Metas |

Regras que valem para quem não é dono:
- **Procedência dos aparelhos** (de quem a loja comprou e por quanto) é **só do dono**: não aparece em tela, comprovante, nota nem vai para a IA.
- **Gastos:** a vendedora lança, vê e corrige, **menos "Compra de aparelho"** (é procedência); não apaga. O técnico não vê gastos.
- Só o dono altera dados da loja, funcionários, metas e paga comissões.
- Essas regras estão **no banco** (Supabase, RLS), não só na tela.

Login: só **usuário e senha** (sem e-mail). Por dentro, o usuário vira `usuario@idsolucoes.app` no Supabase Auth; ninguém recebe e-mail. Usuários são criados pela função `criar_usuario` (só o dono), direto no banco.

## 4. Regras de negócio decididas

- **Comissão do Kaique:** R$ 30 por serviço entregue em que ele é o técnico, **só se o dono não participou** (marcar "Cleisson Fernandes participou" na OS ou na entrega zera a comissão daquele serviço).
- **Comissão da Luciana:** R$ 30 **por aparelho vendido** (venda com 2 iPhones = R$ 60). Venda só de acessórios não conta. (Opção "Comissão de venda só em aparelhos" no cadastro do funcionário.) Ainda a confirmar se era por aparelho ou por venda.
- **Metas** semanais e mensais por pessoa e da loja (aparecem no Painel).
- **Acessórios:** venda ou brinde, com preço tabelado; cada saída registrada.
- **Aparelho recebido** (compra de cliente ou troca no balcão) vai para o estoque de venda como "Em preparação", com condição de chegada, reparos sugeridos (bateria < 85%, tela/tampa trincada etc.), custo total = compra + reparos, preço sugerido pela margem sobre o custo (padrão 30%). Não pode ficar "Disponível" com reparo pendente. Compra de aparelho gera gasto automático.
- **Troca no balcão** exige cliente identificado (fica registrado de quem veio).
- **Modelo do aparelho é livre** (qualquer marca); há sugestões de iPhone, iPad, Mac, Watch, AirPods, iPod etc. Capacidade também livre.
- **Consulta do aparelho:** botão "Consultar aparelho" ao lado do IMEI. Sem serviço pago, mostra "não foi possível consultar automaticamente" e oferece **Anatel · bloqueio** (Celular Legal/ABR Telecom), **Apple · garantia** e **iUnlocker**, abrindo em janela pequena ao lado (no computador), com o número copiado. O resultado colado é lido sozinho. Bloqueio (Anatel ou iCloud) mostra aviso vermelho e impede a troca. A variável `consultaAuto` está pronta para um serviço pago futuro (o dono preferiu ficar no gratuito).
- **CRM (Relacionamento):** filtros (serviço, iPhone, acessório, garantia terminando em 15 dias, sumidos 90+ dias, sem mensagem 60+ dias), modelos de mensagem com {nome} {aparelho} {garantia} {tempo} {ultima} {loja}, envio em sequência pelo WhatsApp (um por um), registro de cada envio, opção "Não quer receber mensagens" (LGPD).
- **Comprovantes** em gastos: foto (reduzida para ~1600 px JPEG) ou PDF até 8 MB, no Supabase Storage, bucket privado `comprovantes`.
- **Logo da loja:** o dono troca sozinho em Configurações › Logo da loja (fica em `loja.logo`, imagem reduzida). Sem logo, aparece o símbolo "iD" padrão.
- **Assistente IA:** modo **Rápido** = `claude-haiku-5-5` (padrão, centavos por pergunta); **Completo** = `claude-opus-5-5` (com fallback de recusa do servidor). Cada pessoa só manda para a IA os dados que pode ver.
- **Nota fiscal:** ainda **em simulação** (sem valor fiscal). Emitir de verdade exige certificado A1 + emissor pago (Focus NFe, NFE.io…). Não implementado.
- **WhatsApp automático** (sem tocar em enviar) exige API oficial paga. Não implementado.

## 5. Como o sistema é feito

- **Um arquivo HTML** com tudo (HTML, CSS e JavaScript puro, sem framework). Telas: Painel, OS, Aparelhos na loja, Vendas/balcão, Aparelhos à venda, Acessórios, Clientes, Funcionários, Gastos, Comissões, Metas, Relacionamento, Notas fiscais, Configurações, Personalizar, Assistente IA.
- `fonte/sistema.html` é a **fonte principal** (também é a versão de demonstração do claude.ai, que guarda dados no navegador).
- `fonte/online.js` é a **camada online**: login, papéis, sincronização com o Supabase, tempo real, usuários, comprovantes no Storage, assistente via função.
- `ferramentas/montar_site.py` junta os dois e gera `site-pronto/index.html` + `site-pronto/id-solucoes-site.zip` (é esse zip que vai para a Cloudflare).

### Banco (Supabase)
- Tabela `public.registros (colecao, id, dados jsonb, atualizado, atualizado_por)`: **cada registro do sistema é uma linha**. Coleções: `config`(id `loja`), `seq`, `clientes`, `iphones`, `procedencias` (separada do aparelho, só dono lê), `acessorios`, `os`, `vendas`, `notas`, `funcionarios`, `metas`, `gastos`, `movs`, `pagamentosCom`, `comPagas`.
- Tabela `public.perfis (usuario, nome, papel dono|tecnico|vendedor, funcionario_id, user_id, ativo)`.
- Funções: `meu_papel()`, `_criar_conta` (interna), `criar_usuario`, `trocar_senha`, `apagar_usuario`.
- Tempo real ligado na tabela `registros` (o que um salva aparece para os outros em segundos).
- Storage: bucket privado `comprovantes` (dono e vendedor leem/enviam; só dono apaga).
- Scripts já rodados no projeto atual, em ordem: `banco/1-usuarios-e-regras.sql` (com a senha do cleisson trocada no fim) e `banco/2-gastos-vendedora-e-comprovantes.sql`. Para um projeto **novo**, use só `banco/instalar-do-zero.sql` (junta os dois, comentado). Todos podem ser rodados de novo sem estragar nada.

### Funcionários no sistema (ids fixos)
`f0` Cleisson Fernandes (dono) · `f1` Kaique (técnico) · `f2` Luciana (vendedora).

## 6. Como fazer uma alteração

1. Mude `fonte/sistema.html` (telas e regras) e/ou `fonte/online.js` (o que só existe online).
2. Rode: `python3 ferramentas/montar_site.py`.
3. Teste (o Claude testa com Playwright usando `ferramentas/mock_supabase.js` e `ferramentas/mock_server.js`, que imitam o Supabase com as mesmas regras do banco).
4. Envie `site-pronto/id-solucoes-site.zip` na Cloudflare (dawn-leaf-c6fb › New deployment). Todos recarregam a página.
5. Se mudar regra de acesso ou estrutura do banco: escreva um SQL que possa rodar de novo sem estragar, teste num Postgres local e entregue para colar no SQL Editor.
6. Para atualizar a demonstração do claude.ai, republicar `fonte/sistema.html` no mesmo link.

Cuidados: não quebrar a migração de dados já salvos (funções `migrar*` no sistema); manter a procedência fora de documentos do cliente; manter textos em português simples.

## 7. Rotina do dono

- Toda semana: **Configurações › Baixar cópia dos dados** e guardar (o plano grátis do Supabase não faz cópia sozinho; fotos dos comprovantes ficam no Storage, fora da cópia).
- O banco grátis pausa após 7 dias sem nenhum uso.
- Limite de gasto da IA: Claude Console › Limites.

## 8. Ideias combinadas para o futuro

- Ligar a Cloudflare ao GitHub para o site se atualizar sozinho (sem enviar zip).
- Trocar o endereço "dawn-leaf-c6fb" por um nome melhor ou domínio próprio (registro.br).
- Nota fiscal real, WhatsApp automático e consulta automática de IMEI (todos pagos) quando o dono quiser.

## 9. Levar o sistema para outro lugar (o código é seu)

Este pacote tem **todo** o código do sistema; não depende do Claude para funcionar.

- **O site** é um arquivo só (`site-pronto/index.html`), HTML e JavaScript puros. Funciona em qualquer hospedagem de site estático: Cloudflare (atual), Netlify, Vercel, GitHub Pages, servidor próprio ou da agência. Basta publicar esse arquivo como `index.html`.
- **O banco e o login** ficam no seu Supabase. Para mudar de hospedagem do site, o banco continua o mesmo. Para sair do Supabase, um programador pode: exportar os dados (Supabase › Database › Backups, ou `pg_dump`), recriar as tabelas com `banco/1-...sql` e `banco/2-...sql` em outro PostgreSQL e trocar a camada `fonte/online.js`, que concentra toda a ligação com o Supabase.
- **A IA** é a função `supabase-funcao/assistente.ts` (padrão Deno/TypeScript), que usa a sua chave da Anthropic. Pode rodar em qualquer servidor que execute Deno ou Node.
- **Os dados** também saem pelo próprio sistema: Configurações › Baixar cópia dos dados (arquivo JSON) e Importar cópia.
- **Versão sem internet/sem login** (guarda dados só no navegador): `fonte/sistema.html`, aberto direto num navegador.

Bibliotecas externas usadas: `@supabase/supabase-js` 2.118.0 (carregada do jsDelivr) e, na função da IA, `@anthropic-ai/sdk` 1.5.0. Fontes Inter e JetBrains Mono (Google Fonts). Sem outras dependências.
