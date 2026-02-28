import os
import subprocess
import tempfile
from pathlib import Path


def converter_docx_para_pdf(docx_path: str) -> str | None:
    """
    Converte .docx para .pdf usando LibreOffice (soffice).
    Retorna o caminho do PDF gerado ou None em caso de falha.
    """
    if not os.path.exists(docx_path):
        return None

    libreoffice = os.environ.get("LIBREOFFICE_PATH", "soffice")
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
            return None

        pdf_name = Path(docx_path).with_suffix(".pdf").name
        pdf_path = os.path.join(output_dir, pdf_name)
        if os.path.exists(pdf_path):
            return pdf_path
        return None
    except Exception:
        return None
