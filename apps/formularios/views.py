from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import LinkFormulario
from .serializers import LinkFormularioSerializer
from apps.clientes.models import Cliente
from apps.contratos.models import Contrato
from services.contrato_service import gerar_contrato_docx
from services.storage_service import fazer_upload_supabase, fazer_upload_supabase_pdf
from services.pdf_service import converter_docx_para_pdf
from services.validacao_service import validar_campos_payload
from services.email_service import enviar_email
from services.auditoria_service import registrar_evento
import os
import tempfile


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def links_list(request):
    org = request.user.organizacao

    if request.method == "GET":
        links = LinkFormulario.objects.filter(organizacao=org).select_related("cliente", "modelo")
        serializer = LinkFormularioSerializer(links, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = LinkFormularioSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        link = serializer.save()
        link_url = request.build_absolute_uri(f"/formulario/{link.token}/")
        enviar_email(
            destinatario=link.cliente.email,
            assunto="Seu formulario de contrato",
            mensagem=(
                f"Ola {link.cliente.nome},\n\n"
                f"Acesse o link para preencher os dados do contrato:\n{link_url}\n\n"
                "Se voce nao reconhece este email, ignore esta mensagem."
            ),
        )
        return Response(LinkFormularioSerializer(link, context={"request": request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def formulario_info(request, token):
    link = get_object_or_404(LinkFormulario, token=token, utilizado=False)
    campos = link.modelo.campos.filter(ativo=True).order_by("ordem", "id")
    return Response({
        "cliente_nome": link.cliente.nome,
        "modelo_nome": link.modelo.nome,
        "token": str(link.token),
        "campos": [
            {
                "placeholder": campo.placeholder,
                "label": campo.label,
                "tipo": campo.tipo,
                "obrigatorio": campo.obrigatorio,
                "mascara": campo.mascara,
                "ajuda": campo.ajuda,
                "opcoes": campo.opcoes,
                "ordem": campo.ordem,
            }
            for campo in campos
        ],
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def receber_formulario(request, token):
    link = get_object_or_404(LinkFormulario, token=token, utilizado=False)
    campos = link.modelo.campos.filter(ativo=True).order_by("ordem", "id")
    if not campos.exists():
        return Response(
            {"erros": ["Nenhum campo configurado para este modelo."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    aceite = request.data.get("aceite_lgpd")
    if not aceite:
        return Response(
            {"erros": ["Voce precisa aceitar os Termos e a Politica de Privacidade."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    valido, dados, erros = validar_campos_payload(campos, request.data)
    if not valido:
        return Response({"erros": erros}, status=status.HTTP_400_BAD_REQUEST)

    cliente = link.cliente

    placeholders = {
        "NOME": cliente.nome,
        "CPF": cliente.cpf,
        "EMAIL": cliente.email,
        "TELEFONE": cliente.telefone,
    }
    placeholders.update(dados)

    try:
        modelo_path = link.modelo.arquivo_docx.path
    except Exception:
        return Response(
            {"erro": "Arquivo do modelo não encontrado no servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        gerar_contrato_docx(modelo_path, placeholders, tmp_path)

        supabase_url = fazer_upload_supabase(
            local_path=tmp_path,
            destino=f"contratos/{link.organizacao.id}/{cliente.id}_{link.token}.docx",
        )

        pdf_path = converter_docx_para_pdf(tmp_path)
        supabase_pdf_url = None
        if pdf_path:
            supabase_pdf_url = fazer_upload_supabase_pdf(
                local_path=pdf_path,
                destino=f"contratos/{link.organizacao.id}/{cliente.id}_{link.token}.pdf",
            )

        contrato = Contrato.objects.create(
            organizacao=link.organizacao,
            cliente=cliente,
            modelo=link.modelo,
            supabase_url=supabase_url or "",
            supabase_pdf_url=supabase_pdf_url or "",
        )

        registrar_evento(
            contrato=contrato,
            acao="contrato_gerado",
            usuario=None,
            detalhes="Gerado via API publica",
        )

        if not supabase_url:
            from django.core.files import File
            with open(tmp_path, "rb") as f:
                contrato.arquivo_docx.save(
                    f"contratos/{cliente.id}_{link.token}.docx",
                    File(f),
                    save=True,
                )

        if pdf_path and not supabase_pdf_url:
            from django.core.files import File
            with open(pdf_path, "rb") as f:
                contrato.arquivo_pdf.save(
                    f"contratos/pdf/{cliente.id}_{link.token}.pdf",
                    File(f),
                    save=True,
                )

        link.utilizado = True
        link.save()

        download_url = supabase_pdf_url or ""
        if not download_url and contrato.arquivo_pdf:
            download_url = request.build_absolute_uri(contrato.arquivo_pdf.url)
        if not download_url:
            download_url = supabase_url or ""

        if download_url:
            enviar_email(
                destinatario=cliente.email,
                assunto="Contrato gerado (PDF)",
                mensagem=(
                    f"Ola {cliente.nome},\n\n"
                    f"Seu contrato foi gerado. Baixe o PDF aqui:\n{download_url}\n\n"
                    "Se voce nao reconhece este email, ignore esta mensagem."
                ),
            )

        return Response({
            "status": "contrato_gerado",
            "contrato_id": str(contrato.id),
            "download_url": download_url,
        })

    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


