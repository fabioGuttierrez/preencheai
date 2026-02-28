import os
from django.conf import settings


def fazer_upload_supabase(local_path: str, destino: str) -> str | None:
    """
    Faz upload de um arquivo para o Supabase Storage.
    Retorna a URL pública ou None se falhar / não configurado.
    """
    try:
        from supabase import create_client

        url = getattr(settings, "SUPABASE_URL", "")
        key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        bucket = getattr(settings, "SUPABASE_BUCKET_CONTRATOS", "contratos-gerados")

        if not url or not key:
            return None

        client = create_client(url, key)

        with open(local_path, "rb") as f:
            conteudo = f.read()

        client.storage.from_(bucket).upload(
            path=destino,
            file=conteudo,
            file_options={"content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        )

        resultado = client.storage.from_(bucket).get_public_url(destino)
        return resultado

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Erro no upload Supabase: {e}")
        return None


def fazer_upload_supabase_pdf(local_path: str, destino: str) -> str | None:
    """
    Faz upload de um PDF para o Supabase Storage.
    Retorna a URL publica ou None se falhar / nao configurado.
    """
    try:
        from supabase import create_client

        url = getattr(settings, "SUPABASE_URL", "")
        key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        bucket = getattr(settings, "SUPABASE_BUCKET_CONTRATOS", "contratos-gerados")

        if not url or not key:
            return None

        client = create_client(url, key)

        with open(local_path, "rb") as f:
            conteudo = f.read()

        client.storage.from_(bucket).upload(
            path=destino,
            file=conteudo,
            file_options={"content-type": "application/pdf"},
        )

        return client.storage.from_(bucket).get_public_url(destino)

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Erro no upload PDF Supabase: {e}")
        return None


def fazer_upload_modelo_supabase(local_path: str, destino: str) -> str | None:
    """
    Faz upload de um modelo .docx para o bucket de modelos no Supabase Storage.
    """
    try:
        from supabase import create_client

        url = getattr(settings, "SUPABASE_URL", "")
        key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        bucket = getattr(settings, "SUPABASE_BUCKET_MODELOS", "modelos-contratos")

        if not url or not key:
            return None

        client = create_client(url, key)

        with open(local_path, "rb") as f:
            conteudo = f.read()

        client.storage.from_(bucket).upload(
            path=destino,
            file=conteudo,
            file_options={"content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        )

        return client.storage.from_(bucket).get_public_url(destino)

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Erro no upload do modelo Supabase: {e}")
        return None
