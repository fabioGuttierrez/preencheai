from django.core.management.base import BaseCommand
from apps.contratos.models import Contrato


class Command(BaseCommand):
    help = "Corrige caminhos duplicados em arquivo_docx e arquivo_pdf"

    def add_arguments(self, parser):
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Aplica as correções (sem esta flag apenas lista os registros afetados)",
        )

    def handle(self, *args, **options):
        aplicar = options["aplicar"]

        docx_errados = Contrato.objects.filter(arquivo_docx__startswith="contratos/contratos/")
        pdf_errados = Contrato.objects.filter(arquivo_pdf__startswith="contratos/pdf/contratos/")

        self.stdout.write(f"arquivo_docx com caminho duplicado: {docx_errados.count()}")
        self.stdout.write(f"arquivo_pdf  com caminho duplicado: {pdf_errados.count()}")

        if not aplicar:
            self.stdout.write(self.style.WARNING("Modo simulação. Use --aplicar para corrigir."))
            for c in docx_errados:
                self.stdout.write(f"  DOCX {c.id}: {c.arquivo_docx.name}")
            for c in pdf_errados:
                self.stdout.write(f"  PDF  {c.id}: {c.arquivo_pdf.name}")
            return

        corrigidos = 0
        for c in docx_errados:
            novo = c.arquivo_docx.name.replace("contratos/contratos/", "contratos/", 1)
            self.stdout.write(f"  DOCX {c.id}: {c.arquivo_docx.name} → {novo}")
            c.arquivo_docx.name = novo
            c.save(update_fields=["arquivo_docx"])
            corrigidos += 1

        for c in pdf_errados:
            novo = c.arquivo_pdf.name.replace("contratos/pdf/contratos/pdf/", "contratos/pdf/", 1)
            self.stdout.write(f"  PDF  {c.id}: {c.arquivo_pdf.name} → {novo}")
            c.arquivo_pdf.name = novo
            c.save(update_fields=["arquivo_pdf"])
            corrigidos += 1

        self.stdout.write(self.style.SUCCESS(f"{corrigidos} registros corrigidos."))
