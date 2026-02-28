# preencheai

SaaS para geracao de contratos com modelos .docx, formulario publico dinamico e exportacao em PDF.

## Proximos passos (checklist)

- Criar uma Organizacao e vincular o usuario (admin).
- Subir o servidor e testar o fluxo completo.
- Garantir o LibreOffice instalado para gerar PDF.
- Ajustar validacoes e mascaras dos campos conforme necessidade.

## Setup rapido

1) Instale dependencias

```
pip install -r requirements.txt
```

2) Configure o arquivo .env

Use o arquivo .env.example como base:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- DATABASE_URL (opcional, default SQLite)
- SUPABASE_* (opcional, apenas se usar storage)

3) Rode migracoes

```
python manage.py migrate
```

4) Crie superusuario

```
python manage.py createsuperuser
```

5) Inicie o servidor

```
python manage.py runserver
```

## Deploy

Veja o guia em [DEPLOY.md](DEPLOY.md).

## Fluxo do produto

1) Cadastro no painel (/cadastro/)
2) Login no painel (/login/)
3) Criar Cliente
4) Upload de Modelo .docx
5) Configurar campos detectados
6) Gerar Link de formulario
7) Cliente preenche formulario publico
8) Contrato gerado e baixado em PDF

## PDF (LibreOffice)

A conversao DOCX -> PDF usa o LibreOffice em modo headless.

Requisitos:
- LibreOffice instalado no servidor
- Executavel disponivel no PATH (comando `soffice`)

Se necessario, defina a variavel de ambiente:

```
LIBREOFFICE_PATH=C:\\Program Files\\LibreOffice\\program\\soffice.exe
```

## Storage (opcional)

Se SUPABASE_* estiver configurado, o PDF e o DOCX podem ser enviados para o Supabase.
Se nao, os arquivos sao salvos em media/ local.

## Email transacional

Configurado via SMTP (Brevo). Ajuste as variaveis EMAIL_* no .env.
O sistema envia emails com link do formulario e download do contrato.

## LGPD

As paginas de Termos e Privacidade estao em /termos/ e /privacidade/.
O formulario publico exige aceite para envio.

## Multi-tenant

Todos os dados sao filtrados por Organizacao do usuario logado.
Se um usuario nao tiver Organizacao, o sistema bloqueia operacoes sensiveis.

## Troubleshooting

- Erro: ModuleNotFoundError: decouple
  - Solucao: `pip install python-decouple`

- Erro: manage.py nao encontrado
  - Rode os comandos dentro da pasta `saas_contratos/`.

- Erro: NOT NULL constraint failed: clientes_cliente.organizacao_id
  - Vincule o usuario a uma Organizacao no admin.

- PDF nao gera
  - Verifique se o LibreOffice esta instalado e `soffice` acessivel.

## Roadmap (futuro)

- Assinatura digital (servico premium)
- Validacao avancada por tipo de campo
- Registro de historico de submissao do formulario
