# AutoContrato

SaaS para geração automática de contratos para eventos.

## Stack
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- PostgreSQL
- Jinja2
- WeasyPrint
- Redis + Celery (opcional)
- Docker
- Coolify
- Nginx
- SMTP profissional

## Funcionalidade de Upload de Templates

Clientes podem fazer upload de múltiplos contratos (PDF, DOCX, HTML) para uso como templates personalizados.
Os arquivos são armazenados por empresa e podem ser convertidos para HTML/Jinja2.
O número de templates e contratos automatizáveis pode ser limitado conforme o plano contratado.

Endpoint:
- POST /admin/template/upload
	- Permite upload de múltiplos arquivos.
	- Armazena arquivos em `app/templates_html/{company_id}/`.

## Docker e Deploy

Para rodar o projeto com Docker:

1. Configure o arquivo `.env` em `app/`.
2. Execute:
	- `docker-compose up --build`
3. O serviço estará disponível em `http://localhost:8000`.

Containers:
- app (FastAPI)
- db (PostgreSQL)
- redis (opcional)

Backup automático do banco pode ser configurado via volumes.

## Estrutura de Pastas
Veja a pasta `app/` para a estrutura profissional recomendada.
