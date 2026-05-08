import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


def converter_docx_para_pdf(docx_path: str) -> str | None:
    """
    Converte .docx para .pdf usando LibreOffice (soffice).
    Retorna o caminho de um arquivo temporário .pdf ou None em caso de falha.
    O chamador é responsável por deletar o arquivo retornado após o uso.
    """
    if not Path(docx_path).exists():
        logger.error("Arquivo DOCX nao encontrado para conversao: %s", docx_path)
        return None

    libreoffice = getattr(settings, "LIBREOFFICE_PATH", "soffice")
    output_dir = tempfile.mkdtemp(prefix="pdf_out_")

    try:
        cmd = [
            libreoffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            docx_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(
                "Falha ao converter DOCX para PDF (code=%s). stdout=%s stderr=%s",
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip(),
            )
            return None

        pdf_in_dir = Path(output_dir) / Path(docx_path).with_suffix(".pdf").name
        if not pdf_in_dir.exists():
            logger.error("PDF nao encontrado apos conversao. esperado=%s", pdf_in_dir)
            return None

        # Move para um arquivo temporário isolado e limpa o output_dir
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_pdf_path = tmp.name
        shutil.move(str(pdf_in_dir), tmp_pdf_path)
        return tmp_pdf_path

    except Exception as exc:
        logger.exception("Erro inesperado na conversao DOCX->PDF: %s", exc)
        return None
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
