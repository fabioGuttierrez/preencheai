from apps.contratos.models import ContratoEvento


def registrar_evento(*, contrato, acao: str, usuario=None, detalhes: str = "") -> None:
    ContratoEvento.objects.create(
        contrato=contrato,
        usuario=usuario,
        acao=acao,
        detalhes=detalhes,
    )
