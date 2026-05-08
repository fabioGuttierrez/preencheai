import os

from django.core.management.base import BaseCommand

from apps.contratos.models import ModeloContrato
from services.contrato_service import validar_consistencia_modelo


class Command(BaseCommand):
    help = "Verifica integridade dos modelos de contrato: arquivos no disco e consistência de placeholders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--org",
            type=int,
            default=None,
            help="Filtrar por ID de organização (padrão: todas).",
        )

    def handle(self, *args, **options):
        org_id = options["org"]
        qs = ModeloContrato.objects.filter(ativo=True)
        if org_id:
            qs = qs.filter(organizacao_id=org_id)

        total = qs.count()
        erros_arquivo = []
        erros_placeholder = []

        self.stdout.write(f"Verificando {total} modelos ativos...\n")

        for modelo in qs.select_related("organizacao"):
            caminho = modelo.arquivo_docx.path if modelo.arquivo_docx else None

            if not caminho or not os.path.exists(caminho):
                erros_arquivo.append(
                    f"  [ARQUIVO] ID={modelo.pk} org={modelo.organizacao_id} "
                    f"nome='{modelo.nome}' path={caminho}"
                )
                continue

            resultado = validar_consistencia_modelo(modelo)
            if not resultado["ok"]:
                linhas = [
                    f"  [PLACEHOLDER] ID={modelo.pk} org={modelo.organizacao_id} nome='{modelo.nome}'"
                ]
                if resultado.get("no_docx_sem_campo"):
                    linhas.append(
                        f"    No docx mas sem CampoTemplate: {resultado['no_docx_sem_campo']}"
                    )
                if resultado.get("no_campo_sem_docx"):
                    linhas.append(
                        f"    CampoTemplate sem placeholder no docx: {resultado['no_campo_sem_docx']}"
                    )
                erros_placeholder.extend(linhas)

        if not erros_arquivo and not erros_placeholder:
            self.stdout.write(self.style.SUCCESS(f"Tudo OK. {total} modelos verificados sem inconsistências."))
            return

        if erros_arquivo:
            self.stdout.write(self.style.ERROR(f"\n{len(erros_arquivo)} modelo(s) com arquivo ausente:"))
            for linha in erros_arquivo:
                self.stdout.write(self.style.ERROR(linha))

        if erros_placeholder:
            self.stdout.write(self.style.WARNING(f"\n{len(erros_placeholder)} modelo(s) com placeholder inconsistente:"))
            for linha in erros_placeholder:
                self.stdout.write(self.style.WARNING(linha))

        total_erros = len(erros_arquivo) + (1 if erros_placeholder else 0)
        self.stdout.write(f"\nTotal de problemas encontrados: {total_erros}")
