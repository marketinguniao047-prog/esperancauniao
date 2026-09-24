# Site União — Vercel

Esta versão foi preparada para testes na Vercel.

## Importante

A Vercel possui filesystem somente-leitura. Por isso, quando a variável `VERCEL` estiver presente:

- o SQLite é criado em `/tmp/site-uniao/instance/site.db`;
- uploads temporários são gravados em `/tmp/site-uniao/uploads`.

Esses arquivos **não são permanentes**. Esta configuração serve para demonstração/teste. Para produção, use PostgreSQL e armazenamento persistente (ex.: objeto/S3 ou serviço equivalente).

## Login inicial

- E-mail: `admin@uniao.local`
- Senha: `admin123`

Troque a senha antes de qualquer uso real.

## Teste

Após o deploy:

- Site: `https://SEU-PROJETO.vercel.app/`
- Saúde: `https://SEU-PROJETO.vercel.app/health`
- Administração: `https://SEU-PROJETO.vercel.app/admin/login`
