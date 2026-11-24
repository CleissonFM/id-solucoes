-- ID Soluções · Bancada · versão 2: usuários criados pelo administrador, só usuário e senha
-- ANTES DE CLICAR EM RUN: troque TROQUE_AQUI (última parte) pela senha que você quer usar.

create extension if not exists pgcrypto with schema extensions;

-- tabelas (se já existirem, ficam como estão)
create table if not exists public.perfis (
  usuario text primary key,
  nome text not null,
  papel text not null check (papel in ('dono','tecnico','vendedor')),
  funcionario_id text,
  user_id uuid unique,
  ativo boolean not null default true,
  criado timestamptz not null default now()
);
create table if not exists public.registros (
  colecao text not null,
  id text not null,
  dados jsonb not null,
  atualizado timestamptz not null default now(),
  atualizado_por uuid default auth.uid(),
  primary key (colecao, id)
);

-- o "Primeiro acesso" deixa de existir
drop trigger if exists liga_usuario on auth.users;
drop function if exists public.liga_usuario();
drop function if exists public.liberar_senha(text);

create or replace function public.meu_papel() returns text
language sql stable security definer set search_path = public as $$
  select papel from public.perfis where user_id = auth.uid() and ativo
$$;

-- cria a conta (uso interno)
create or replace function public._criar_conta(u text, n text, p text, f text, senha text) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare uid uuid := gen_random_uuid(); em text;
begin
  u := lower(trim(u));
  if u !~ '^[a-z0-9._-]{2,30}$' then raise exception 'Usuário inválido: use só letras minúsculas e números, sem espaço.'; end if;
  if length(coalesce(senha,'')) < 6 then raise exception 'A senha precisa ter pelo menos 6 caracteres.'; end if;
  em := u || '@idsolucoes.app';
  delete from auth.users where email = em;
  insert into auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at,
      raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
      confirmation_token, recovery_token, email_change_token_new, email_change,
      email_change_token_current, phone_change, phone_change_token, reauthentication_token)
    values ('00000000-0000-0000-0000-000000000000', uid, 'authenticated', 'authenticated', em,
      crypt(senha, gen_salt('bf')), now(),
      '{"provider":"email","providers":["email"]}', jsonb_build_object('usuario', u), now(), now(),
      '', '', '', '', '', '', '', '');
  insert into auth.identities (id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
    values (gen_random_uuid(), uid, uid::text,
      jsonb_build_object('sub', uid::text, 'email', em, 'email_verified', true), 'email', now(), now(), now());
  insert into public.perfis (usuario, nome, papel, funcionario_id, user_id, ativo)
    values (u, n, p, nullif(f,''), uid, true)
    on conflict (usuario) do update set nome = excluded.nome, papel = excluded.papel,
      funcionario_id = excluded.funcionario_id, user_id = excluded.user_id, ativo = true;
end $$;
revoke all on function public._criar_conta(text,text,text,text,text) from public, anon, authenticated;

-- administrador cria usuário (técnico ou vendedor)
create or replace function public.criar_usuario(u text, n text, p text, f text, senha text) returns void
language plpgsql security definer set search_path = public as $$
begin
  if public.meu_papel() is distinct from 'dono' then raise exception 'Só o administrador pode criar usuários.'; end if;
  if p not in ('tecnico','vendedor') then raise exception 'Função inválida.'; end if;
  if exists (select 1 from public.perfis where usuario = lower(trim(u))) then raise exception 'Esse usuário já existe.'; end if;
  perform public._criar_conta(u, n, p, f, senha);
end $$;

-- administrador troca a senha de alguém; cada um pode trocar a própria
create or replace function public.trocar_senha(u text, senha text) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare alvo uuid;
begin
  select user_id into alvo from public.perfis where usuario = lower(trim(u));
  if alvo is null then raise exception 'Usuário não encontrado.'; end if;
  if public.meu_papel() is distinct from 'dono' and alvo is distinct from auth.uid() then raise exception 'Você só pode trocar a sua própria senha.'; end if;
  if length(coalesce(senha,'')) < 6 then raise exception 'A senha precisa ter pelo menos 6 caracteres.'; end if;
  update auth.users set encrypted_password = crypt(senha, gen_salt('bf')), updated_at = now() where id = alvo;
end $$;

-- administrador apaga usuário (os registros que ele lançou continuam no sistema)
create or replace function public.apagar_usuario(u text) returns void
language plpgsql security definer set search_path = public as $$
declare alvo uuid;
begin
  if public.meu_papel() is distinct from 'dono' then raise exception 'Só o administrador pode apagar usuários.'; end if;
  select user_id into alvo from public.perfis where usuario = lower(trim(u));
  if alvo = auth.uid() then raise exception 'Você não pode apagar o seu próprio usuário.'; end if;
  delete from public.perfis where usuario = lower(trim(u));
  if alvo is not null then delete from auth.users where id = alvo; end if;
end $$;

-- regras de acesso
alter table public.perfis enable row level security;
alter table public.registros enable row level security;

drop policy if exists perfis_ler on public.perfis;
drop policy if exists perfis_dono on public.perfis;
create policy perfis_ler on public.perfis for select to authenticated using (true);
create policy perfis_dono on public.perfis for update to authenticated
  using (public.meu_papel() = 'dono') with check (public.meu_papel() = 'dono');

drop policy if exists reg_ler on public.registros;
drop policy if exists reg_criar on public.registros;
drop policy if exists reg_alterar on public.registros;
drop policy if exists reg_apagar on public.registros;
create policy reg_ler on public.registros for select to authenticated using (
  public.meu_papel() = 'dono'
  or (public.meu_papel() is not null and colecao not in ('procedencias','gastos'))
);
create policy reg_criar on public.registros for insert to authenticated with check (
  public.meu_papel() = 'dono'
  or (public.meu_papel() is not null and colecao not in ('config','funcionarios','metas','comPagas','pagamentosCom'))
);
create policy reg_alterar on public.registros for update to authenticated
  using (
    public.meu_papel() = 'dono'
    or (public.meu_papel() is not null and colecao not in ('config','funcionarios','metas','comPagas','pagamentosCom','procedencias','gastos'))
  )
  with check (
    public.meu_papel() = 'dono'
    or (public.meu_papel() is not null and colecao not in ('config','funcionarios','metas','comPagas','pagamentosCom','procedencias','gastos'))
  );
create policy reg_apagar on public.registros for delete to authenticated using (public.meu_papel() = 'dono');

do $$ begin
  alter publication supabase_realtime add table public.registros;
exception when duplicate_object then null; end $$;

-- os outros usuários agora são criados por você dentro do sistema
delete from public.perfis where usuario <> 'cleisson' and user_id is null;

-- ===== SEU USUÁRIO DE ADMINISTRADOR =====
do $$
declare senha text := 'TROQUE_AQUI';
begin
  if senha = 'TROQUE_AQUI' then raise exception 'Troque TROQUE_AQUI pela sua senha antes de clicar em Run.'; end if;
  perform public._criar_conta('cleisson', 'Cleisson Fernandes', 'dono', 'f0', senha);
end $$;
