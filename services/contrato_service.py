import re
from docx import Document


def gerar_contrato_docx(modelo_path: str, dados: dict, output_path: str) -> None:
    """
    Abre o modelo .docx, substitui todos os placeholders {{CHAVE}}
    pelos valores em `dados` e salva em output_path.
    """
    doc = Document(modelo_path)

    def substituir_runs(paragraph):
        # Reconstrói o texto completo do parágrafo para detectar placeholders
        # quebrados entre runs
        full_text = "".join(run.text for run in paragraph.runs)
        modified = False

        for chave, valor in dados.items():
            placeholder = f"{{{{{chave}}}}}"
            if placeholder in full_text:
                full_text = full_text.replace(placeholder, str(valor))
                modified = True

        if modified:
            # Coloca o texto completo no primeiro run e limpa os demais
            if paragraph.runs:
                paragraph.runs[0].text = full_text
                for run in paragraph.runs[1:]:
                    run.text = ""

    for paragraph in doc.paragraphs:
        substituir_runs(paragraph)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    substituir_runs(paragraph)

    doc.save(output_path)


def extrair_placeholders_docx(modelo_path: str) -> list[str]:
    """
    Retorna uma lista unica de placeholders encontrados no .docx, sem chaves.
    Ex.: {{NOME}} => "NOME"
    """
    doc = Document(modelo_path)
    encontrados = set()
    padrao = re.compile(r"\{\{\s*([^{}\s]+)\s*\}\}")

    def coletar_texto(paragraph):
        texto = "".join(run.text for run in paragraph.runs)
        for match in padrao.findall(texto):
            encontrados.add(match.strip())

    for paragraph in doc.paragraphs:
        coletar_texto(paragraph)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    coletar_texto(paragraph)

    return sorted(encontrados)
