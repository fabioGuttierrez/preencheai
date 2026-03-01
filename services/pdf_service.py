import logging
import subprocess
import tempfile
from pathlib import Path
from django.conf import settings


def converter_docx_para_pdf(docx_path: str) -> str | None:
    """
    Converte .docx para .pdf usando LibreOffice (soffice).
    Retorna o caminho do PDF gerado ou None em caso de falha.
    """
    logger = logging.getLogger(__name__)
    if not Path(docx_path).exists():
        logger.error("Arquivo DOCX nao encontrado para conversao: %s", docx_path)
        return None

    libreoffice = getattr(settings, "LIBREOFFICE_PATH", "soffice")
    output_dir = tempfile.mkdtemp(prefix="pdf_out_")

    cmd = [
        libreoffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        docx_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(
                "Falha ao converter DOCX para PDF (code=%s). stdout=%s stderr=%s",
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip(),
            )
            return None

        pdf_name = Path(docx_path).with_suffix(".pdf").name
        pdf_path = Path(output_dir) / pdf_name
        if pdf_path.exists():
            return str(pdf_path)
        logger.error("PDF nao encontrado apos conversao. esperado=%s", pdf_path)
        return None
    except Exception as exc:
        logger.exception("Erro inesperado na conversao DOCX->PDF: %s", exc)
        return None
