from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from services.pdf_service import converter_docx_para_pdf


class Command(BaseCommand):
    help = "Converte um DOCX em PDF para testar o LibreOffice."

    def add_arguments(self, parser):
        parser.add_argument("docx_path", help="Caminho absoluto ou relativo do .docx")

    def handle(self, *args, **options):
        docx_path = Path(options["docx_path"]).expanduser()
        if not docx_path.is_absolute():
            docx_path = (Path.cwd() / docx_path).resolve()

        if not docx_path.exists():
            raise CommandError(f"Arquivo nao encontrado: {docx_path}")

        pdf_path = converter_docx_para_pdf(str(docx_path))
        if not pdf_path:
            raise CommandError("Falha ao converter DOCX para PDF. Verifique os logs.")

        self.stdout.write(self.style.SUCCESS(f"PDF gerado: {pdf_path}"))
