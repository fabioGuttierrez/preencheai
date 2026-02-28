# Deploy (Producao)

Guia rapido para subir o preencheai em producao.

## 1) Variaveis de ambiente

Defina no ambiente:

- SECRET_KEY
- DEBUG=False
- ALLOWED_HOSTS
- DATABASE_URL (SQLite ou Postgres)
- SUPABASE_* (opcional)
- EMAIL_* (Brevo)
- LIBREOFFICE_PATH (se necessario)

## 2) Dependencias do sistema

- Python 3.11+
- LibreOffice (para gerar PDF)

No Linux, normalmente basta instalar o pacote `libreoffice`.

## 3) Instalar dependencias Python

```
pip install -r requirements.txt
```

## 4) Migracoes e static

```
python manage.py migrate
python manage.py collectstatic
```

## 5) Executar com Gunicorn

```
gunicorn saas_contratos.wsgi:application --bind 0.0.0.0:8000

No Coolify, prefira usar o start script:

```
bash start.sh
```
```

Use um process manager (systemd, supervisor) ou container.

## 6) Reverse proxy

Configure Nginx/Apache para TLS e proxy:

- HTTP -> HTTPS
- Proxy para 127.0.0.1:8000
- Servir /static/ e /media/

## 7) Teste final

- Login
- Upload de modelo
- Gerar link
- Gerar contrato e baixar PDF

## Observacoes sobre PDF

- O `soffice` precisa estar disponivel no PATH.
- Se nao estiver, defina `LIBREOFFICE_PATH` com o caminho completo do executavel.
