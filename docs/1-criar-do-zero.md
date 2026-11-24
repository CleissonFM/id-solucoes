# 1. Criar o sistema do zero (passo a passo)

Use este guia para montar o sistema num lugar novo: outra conta, outro projeto ou uma cópia de teste. Leva cerca de 30 minutos. Não precisa saber programar.

Você vai precisar de 3 contas gratuitas (e de uma 4ª, paga por uso, só se quiser o Assistente de IA):

| Conta | Para quê | Custo |
|---|---|---|
| **Supabase** | banco de dados, login e fotos dos comprovantes | grátis (até 500 MB de dados e 1 GB de arquivos) |
| **Cloudflare** | deixar o site no ar | grátis |
| **GitHub** | guardar o código com histórico | grátis |
| Anthropic (Claude Console) | Assistente de IA (opcional) | crédito pré-pago, a partir de US$ 5 |

---

## Parte A · Banco de dados (Supabase)

### A1. Criar o projeto
1. Acesse https://supabase.com/dashboard e entre (pode ser com o GitHub).
2. Clique em **New project**.
3. **Name:** `id-solucoes` · **Database Password:** clique em **Generate a password** e guarde · **Region:** a mais próxima (ex.: South America · São Paulo).
4. Clique em **Create new project** e espere uns 2 minutos.

### A2. Criar as tabelas, as regras e o administrador
1. No menu da esquerda, abra **SQL Editor** › **New query**.
2. Abra o arquivo `banco/instalar-do-zero.sql` deste projeto, copie tudo e cole.
3. **No final do texto**, troque `TROQUE_AQUI` pela senha do administrador (mínimo 6 caracteres).
4. Clique em **Run**. Deve aparecer **Success. No rows returned**.

> Se aparecer "Troque TROQUE_AQUI pela sua senha", é só fazer o item 3 e rodar de novo.
> O texto pode ser rodado várias vezes sem estragar nada.

O que esse texto cria (todas as partes têm comentários dentro do arquivo):
- tabela `perfis` (quem entra e com qual papel) e tabela `registros` (todos os dados do sistema);
- login com **usuário e senha, sem e-mail**;
- regras de quem vê o quê (procedência e gastos protegidos);
- tempo real (o que um salva aparece para os outros);
- espaço privado `comprovantes` para fotos e PDFs;
- o usuário administrador `cleisson`.

### A3. Pegar o endereço e a chave pública
1. **Project Settings** (engrenagem) › **Data API**: copie a **Project URL** (ex.: `https://abcd.supabase.co`).
2. **Project Settings** › **API Keys**: copie a chave **Publishable** (começa com `sb_publishable_`).
   ⚠️ Nunca use nem compartilhe a chave **Secret / service_role**.

### A4. Colocar o endereço e a chave no código
Abra `fonte/online.js` e, na primeira linha útil, troque os valores de `url` e `key`:
```js
const ONLINE={url:'https://SEU-PROJETO.supabase.co',key:'sb_publishable_SUA_CHAVE',dominio:'idsolucoes.app'};
```
Se for um projeto diferente, troque também a chave pública dentro de `supabase-funcao/assistente.ts` (linha do `SUPABASE_ANON_KEY ||`).

---

## Parte B · Montar o site

O site final é **um arquivo só**: `site-pronto/index.html`. Ele é gerado juntando `fonte/sistema.html` (o sistema) com `fonte/online.js` (login e banco).

1. Instale o Python 3 (no Mac já vem instalado; no Windows: https://www.python.org/downloads/).
2. Abra o Terminal na pasta do projeto e rode:
   ```bash
   python3 ferramentas/montar_site.py
   ```
3. Ele gera `site-pronto/index.html` e `site-pronto/id-solucoes-site.zip`.

> O `site-pronto/` deste repositório já está montado com a versão atual; só precisa remontar se mudar algo em `fonte/`.

---

## Parte C · Colocar o site no ar (Cloudflare)

### Primeira vez
1. Acesse https://dash.cloudflare.com e entre.
2. Menu **Workers & Pages** › **Create** › escolha **Upload your static files** (ou "Drag and drop your files").
3. Dê um nome (ex.: `id-solucoes`) e envie o `site-pronto/id-solucoes-site.zip` (sem descompactar).
4. Clique em **Deploy**. O endereço aparece no fim (ex.: `https://id-solucoes.SEUNOME.workers.dev`).

### Atualizações
Abra o projeto na Cloudflare › **New deployment** › envie o zip novo. Depois todos recarregam a página.

### (Opcional) Atualizar sozinho pelo GitHub
Na Cloudflare, crie o projeto com **Connect to Git** escolhendo este repositório e a pasta de saída `site-pronto`. A cada alteração enviada ao GitHub, o site se atualiza sozinho.

---

## Parte D · Primeiro acesso e equipe
1. Abra o endereço do site e entre com o usuário `cleisson` e a senha da Parte A2.
2. **Configurações:** confira os dados da empresa e envie a **logo** (Configurações › Logo da loja).
3. **Funcionários:** confira a equipe (Kaique e Luciana já vêm cadastrados com as comissões).
4. **Funcionários › Usuários do sistema › Novo usuário:** crie o acesso de cada pessoa (usuário, senha, função e funcionário ligado). Passe o endereço, o usuário e a senha para ela.

---

## Parte E · Assistente de IA (opcional)

### E1. Conta e chave
1. Acesse https://platform.claude.com, crie a conta e coloque crédito (Billing, mínimo US$ 5).
2. Recomendado: em **Limits**, defina um limite mensal (ex.: US$ 10) e deixe a recarga automática desligada.
3. **API Keys** › **Create Key** › "Em outro lugar" › copie a chave (`sk-ant-...`). Ela só aparece uma vez.

### E2. Guardar a chave no Supabase
Supabase › **Edge Functions** › **Secrets** › Name `ANTHROPIC_API_KEY`, Value = a chave › **Save**.

### E3. Criar a função
1. Supabase › **Edge Functions** › **Deploy a new function** › **Via Editor**.
2. Nome: `assistente` (exatamente assim).
3. Apague o exemplo, cole o conteúdo de `supabase-funcao/assistente.ts` e clique em **Deploy function**.
4. Na página da função, desligue **Verify JWT** e salve (a própria função confere o login).

Pronto: o botão **Assistente** do sistema passa a responder. Modo **Rápido** custa menos de 1 centavo por pergunta; **Completo**, por volta de R$ 0,50 a R$ 1,00.

---

## Parte F · Guardar no GitHub
1. https://github.com/new › nome `id-solucoes` › **Private** › Create repository.
2. Envie a pasta do projeto (pelo GitHub Desktop, pelo Terminal com `git`, ou pedindo ao Claude).

---

## Cuidados
- **Cópia de segurança:** o plano grátis do Supabase não faz cópia automática. Baixe toda semana em Configurações › Baixar cópia dos dados.
- O banco grátis **pausa após 7 dias sem uso**; basta entrar no painel do Supabase e reativar.
- Nenhuma senha ou chave secreta fica no código. Elas ficam só no Supabase e na Anthropic.
