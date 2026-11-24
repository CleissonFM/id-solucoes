-- ID Soluções · atualização: vendedora lança gastos + comprovantes (fotos e PDF)

-- leitura: procedência só o dono; gastos o dono e a vendedora (menos compra de aparelho)
drop policy if exists reg_ler on public.registros;
create policy reg_ler on public.registros for select to authenticated using (
  public.meu_papel() = 'dono'
  or (public.meu_papel() is not null and colecao not in ('procedencias','gastos'))
  or (public.meu_papel() = 'vendedor' and colecao = 'gastos'
      and coalesce(dados->>'categoria','') <> 'Compra de aparelho')
);

-- alteração: igual, e a vendedora pode corrigir gastos (menos compra de aparelho)
drop policy if exists reg_alterar on public.registros;
create policy reg_alterar on public.registros for update to authenticated
  using (
    public.meu_papel() = 'dono'
    or (public.meu_papel() is not null and colecao not in ('config','funcionarios','metas','comPagas','pagamentosCom','procedencias','gastos'))
    or (public.meu_papel() = 'vendedor' and colecao = 'gastos' and coalesce(dados->>'categoria','') <> 'Compra de aparelho')
  )
  with check (
    public.meu_papel() = 'dono'
    or (public.meu_papel() is not null and colecao not in ('config','funcionarios','metas','comPagas','pagamentosCom','procedencias','gastos'))
    or (public.meu_papel() = 'vendedor' and colecao = 'gastos' and coalesce(dados->>'categoria','') <> 'Compra de aparelho')
  );

-- espaço privado para os comprovantes
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('comprovantes', 'comprovantes', false, 8388608, array['image/jpeg','image/png','image/webp','application/pdf'])
on conflict (id) do update set public = false, file_size_limit = 8388608,
  allowed_mime_types = array['image/jpeg','image/png','image/webp','application/pdf'];

drop policy if exists comprovantes_ler on storage.objects;
drop policy if exists comprovantes_enviar on storage.objects;
drop policy if exists comprovantes_apagar on storage.objects;
create policy comprovantes_ler on storage.objects for select to authenticated
  using (bucket_id = 'comprovantes' and public.meu_papel() in ('dono','vendedor'));
create policy comprovantes_enviar on storage.objects for insert to authenticated
  with check (bucket_id = 'comprovantes' and public.meu_papel() in ('dono','vendedor'));
create policy comprovantes_apagar on storage.objects for delete to authenticated
  using (bucket_id = 'comprovantes' and public.meu_papel() = 'dono');
