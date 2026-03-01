from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone

from apps.clientes.models import Cliente
from apps.contratos.models import ModeloContrato, Contrato, CampoTemplate
from apps.formularios.models import LinkFormulario
from apps.core.models import Organizacao, Usuario
from services.contrato_service import extrair_placeholders_docx
from services.email_service import enviar_email
from services.auditoria_service import registrar_evento
from services.validacao_service import validar_campos_post


def landing(request):
    return render(request, "landing.html")


def termos_view(request):
    return render(request, "termos.html")


def privacidade_view(request):
    return render(request, "privacidade.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")


def cadastro_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        organizacao_nome = request.POST.get("organizacao_nome", "").strip()
        cnpj = request.POST.get("cnpj", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        if not organizacao_nome or not username or not email or not password:
            messages.error(request, "Preencha todos os campos obrigatorios.")
            return render(request, "cadastro.html")

        if password != password2:
            messages.error(request, "As senhas nao conferem.")
            return render(request, "cadastro.html")

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuario ja em uso.")
            return render(request, "cadastro.html")

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "E-mail ja cadastrado.")
            return render(request, "cadastro.html")

        org = Organizacao.objects.create(nome=organizacao_nome, cnpj=cnpj)
        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            organizacao=org,
        )
        login(request, user)
        messages.success(request, "Cadastro realizado com sucesso.")
        return redirect("dashboard")

    return render(request, "cadastro.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    org = request.user.organizacao
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_clientes = Cliente.objects.filter(organizacao=org).count()
    total_contratos = Contrato.objects.filter(organizacao=org).count()
    contratos_mes = Contrato.objects.filter(organizacao=org, criado_em__gte=inicio_mes).count()
    links_pendentes = LinkFormulario.objects.filter(organizacao=org, utilizado=False).count()
    contratos_recentes = Contrato.objects.filter(organizacao=org).select_related("cliente", "modelo").order_by("-criado_em")[:5]
    mostrar_onboarding = total_contratos == 0 and total_clientes == 0

    return render(request, "dashboard.html", {
        "total_clientes": total_clientes,
        "total_contratos": total_contratos,
        "contratos_mes": contratos_mes,
        "links_pendentes": links_pendentes,
        "contratos_recentes": contratos_recentes,
        "mostrar_onboarding": mostrar_onboarding,
    })


# ─── Clientes ────────────────────────────────────────────────────────────────

@login_required
def clientes_lista(request):
    org = request.user.organizacao
    q = request.GET.get("q", "").strip()
    clientes = Cliente.objects.filter(organizacao=org)
    if q:
        clientes = clientes.filter(nome__icontains=q) | clientes.filter(email__icontains=q)
    clientes = clientes.order_by("-criado_em")
    return render(request, "clientes/lista.html", {"clientes": clientes, "q": q})


@login_required
def cliente_criar(request):
    if not request.user.organizacao:
        messages.error(request, "Seu usuario precisa estar vinculado a uma organizacao.")
        return redirect("dashboard")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        cpf = request.POST.get("cpf", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        if not nome or not cpf or not email:
            messages.error(request, "Nome, CPF e e-mail são obrigatórios.")
        else:
            Cliente.objects.create(
                organizacao=request.user.organizacao,
                nome=nome, cpf=cpf, email=email, telefone=telefone,
            )
            messages.success(request, f"Cliente {nome} criado com sucesso.")
            return redirect("clientes_lista")

    return render(request, "clientes/form.html", {"acao": "Criar"})


@login_required
def cliente_editar(request, pk):
    org = request.user.organizacao
    cliente = get_object_or_404(Cliente, pk=pk, organizacao=org)

    if request.method == "POST":
        cliente.nome = request.POST.get("nome", "").strip()
        cliente.cpf = request.POST.get("cpf", "").strip()
        cliente.email = request.POST.get("email", "").strip()
        cliente.telefone = request.POST.get("telefone", "").strip()
        cliente.save()
        messages.success(request, "Cliente atualizado.")
        return redirect("clientes_lista")

    return render(request, "clientes/form.html", {"acao": "Editar", "cliente": cliente})


@login_required
def cliente_deletar(request, pk):
    org = request.user.organizacao
    cliente = get_object_or_404(Cliente, pk=pk, organizacao=org)
    if request.method == "POST":
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f"Cliente {nome} removido.")
    return redirect("clientes_lista")


# ─── Modelos de Contrato ─────────────────────────────────────────────────────

@login_required
def modelos_lista(request):
    org = request.user.organizacao
    modelos = ModeloContrato.objects.filter(organizacao=org, ativo=True).order_by("-criado_em")
    return render(request, "contratos/modelos.html", {"modelos": modelos})


@login_required
def modelo_upload(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        arquivo = request.FILES.get("arquivo_docx")

        if not nome or not arquivo:
            messages.error(request, "Nome e arquivo são obrigatórios.")
        elif not arquivo.name.endswith(".docx"):
            messages.error(request, "Apenas arquivos .docx são aceitos.")
        else:
            modelo = ModeloContrato.objects.create(
                organizacao=request.user.organizacao,
                nome=nome,
                arquivo_docx=arquivo,
            )
            placeholders = []
            try:
                placeholders = extrair_placeholders_docx(modelo.arquivo_docx.path)
            except Exception:
                placeholders = []

            for ordem, placeholder in enumerate(placeholders, start=1):
                CampoTemplate.objects.get_or_create(
                    modelo=modelo,
                    placeholder=placeholder,
                    defaults={
                        "label": _placeholder_para_label(placeholder),
                        "tipo": _inferir_tipo_placeholder(placeholder),
                        "obrigatorio": _placeholder_obrigatorio(placeholder),
                        "ordem": ordem,
                    },
                )

            if placeholders:
                messages.success(request, f"Modelo '{nome}' enviado e campos detectados.")
                return redirect("modelo_campos_config", pk=modelo.pk)

            messages.warning(request, "Modelo enviado, mas nenhum placeholder foi encontrado.")
            return redirect("modelos_lista")

    return render(request, "contratos/modelo_upload.html")


@login_required
def modelo_deletar(request, pk):
    org = request.user.organizacao
    modelo = get_object_or_404(ModeloContrato, pk=pk, organizacao=org)
    if request.method == "POST":
        modelo.ativo = False
        modelo.save()
        messages.success(request, f"Modelo '{modelo.nome}' removido.")
    return redirect("modelos_lista")


@login_required
def modelo_campos_config(request, pk):
    org = request.user.organizacao
    modelo = get_object_or_404(ModeloContrato, pk=pk, organizacao=org)
    campos = modelo.campos.filter(ativo=True).order_by("ordem", "id")

    if request.method == "POST":
        for campo in campos:
            campo.label = request.POST.get(f"label_{campo.id}", campo.label).strip() or campo.label
            campo.tipo = request.POST.get(f"tipo_{campo.id}", campo.tipo)
            campo.obrigatorio = request.POST.get(f"obrigatorio_{campo.id}") == "on"
            campo.mascara = request.POST.get(f"mascara_{campo.id}", "").strip()
            campo.ajuda = request.POST.get(f"ajuda_{campo.id}", "").strip()
            opcoes_raw = request.POST.get(f"opcoes_{campo.id}", "").strip()
            campo.opcoes = _parse_opcoes(opcoes_raw)
            ordem_raw = request.POST.get(f"ordem_{campo.id}", str(campo.ordem)).strip()
            campo.ordem = int(ordem_raw) if ordem_raw.isdigit() else campo.ordem
            campo.save()

        messages.success(request, "Campos atualizados com sucesso.")
        return redirect("modelo_campos_config", pk=modelo.pk)

    return render(request, "contratos/campos_config.html", {
        "modelo": modelo,
        "campos": campos,
        "tipos": CampoTemplate.TIPOS,
    })


# ─── Contratos Gerados ────────────────────────────────────────────────────────

@login_required
def contratos_lista(request):
    org = request.user.organizacao
    contratos = Contrato.objects.filter(organizacao=org).select_related("cliente", "modelo").order_by("-criado_em")
    return render(request, "contratos/lista.html", {"contratos": contratos})


# ─── Links de Formulário ──────────────────────────────────────────────────────

@login_required
def links_lista(request):
    org = request.user.organizacao
    links = LinkFormulario.objects.filter(organizacao=org).select_related("cliente", "modelo").order_by("-criado_em")
    return render(request, "links/lista.html", {"links": links})


@login_required
def link_criar(request):
    org = request.user.organizacao
    clientes = Cliente.objects.filter(organizacao=org).order_by("nome")
    modelos = ModeloContrato.objects.filter(organizacao=org, ativo=True).order_by("nome")

    if request.method == "POST":
        cliente_id = request.POST.get("cliente_id")
        modelo_id = request.POST.get("modelo_id")

        try:
            cliente = Cliente.objects.get(pk=cliente_id, organizacao=org)
            modelo = ModeloContrato.objects.get(pk=modelo_id, organizacao=org, ativo=True)
        except (Cliente.DoesNotExist, ModeloContrato.DoesNotExist):
            messages.error(request, "Cliente ou modelo inválido.")
            return render(request, "links/criar.html", {"clientes": clientes, "modelos": modelos})

        link = LinkFormulario.objects.create(
            organizacao=org, cliente=cliente, modelo=modelo,
        )
        link_url = request.build_absolute_uri(f"/formulario/{link.token}/")
        enviar_email(
            destinatario=cliente.email,
            assunto="Seu formulario de contrato",
            mensagem=(
                f"Ola {cliente.nome},\n\n"
                f"Acesse o link para preencher os dados do contrato:\n{link_url}\n\n"
                "Se voce nao reconhece este email, ignore esta mensagem."
            ),
        )
        messages.success(request, "Link gerado com sucesso!")
        return redirect("link_detalhe", token=link.token)

    return render(request, "links/criar.html", {"clientes": clientes, "modelos": modelos})


@login_required
def link_detalhe(request, token):
    org = request.user.organizacao
    link = get_object_or_404(LinkFormulario, token=token, organizacao=org)
    link_url = request.build_absolute_uri(f"/formulario/{link.token}/")
    return render(request, "links/detalhe.html", {"link": link, "link_url": link_url})


# ─── Formulário Público ───────────────────────────────────────────────────────

def formulario_publico(request, token):
    from apps.contratos.models import Contrato
    from services.contrato_service import gerar_contrato_docx
    from services.storage_service import fazer_upload_supabase, fazer_upload_supabase_pdf
    from services.pdf_service import converter_docx_para_pdf
    from django.core.files import File
    import tempfile, os

    link = get_object_or_404(LinkFormulario, token=token, utilizado=False)
    sucesso = False
    download_url = ""
    campos = link.modelo.campos.filter(ativo=True).order_by("ordem", "id")

    if request.method == "POST":
        if not campos:
            messages.error(request, "Nenhum campo foi configurado para este contrato.")
            return render(request, "formulario_publico.html", {
                "link": link,
                "sucesso": False,
                "download_url": "",
                "campos": campos,
            })

        if not request.POST.get("aceite_lgpd"):
            messages.error(request, "Voce precisa aceitar os Termos e a Politica de Privacidade.")
            return render(request, "formulario_publico.html", {
                "link": link,
                "sucesso": False,
                "download_url": "",
                "campos": campos,
            })

        valido, dados, erros = validar_campos_post(campos, request.POST)
        if not valido:
            for erro in erros:
                messages.error(request, erro)
        else:
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
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                    tmp_path = tmp.name

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
                else:
                    messages.warning(
                        request,
                        "PDF nao gerado. Verifique se o LibreOffice esta instalado e LIBREOFFICE_PATH configurado.",
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
                    detalhes="Gerado via formulario publico",
                )

                if not supabase_url:
                    with open(tmp_path, "rb") as f:
                        contrato.arquivo_docx.save(
                            f"contratos/{cliente.id}_{link.token}.docx",
                            File(f), save=True,
                        )
                if pdf_path:
                    if not supabase_pdf_url:
                        with open(pdf_path, "rb") as f:
                            contrato.arquivo_pdf.save(
                                f"contratos/pdf/{cliente.id}_{link.token}.pdf",
                                File(f), save=True,
                            )
                        download_url = request.build_absolute_uri(contrato.arquivo_pdf.url)
                    else:
                        download_url = supabase_pdf_url
                elif supabase_url:
                    download_url = supabase_url
                elif contrato.arquivo_docx:
                    download_url = request.build_absolute_uri(contrato.arquivo_docx.url)

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

                if pdf_path and os.path.exists(pdf_path):
                    os.remove(pdf_path)
                os.remove(tmp_path)
                link.utilizado = True
                link.save()
                sucesso = True

            except Exception as e:
                messages.error(request, f"Erro ao gerar contrato: {str(e)}")

    return render(request, "formulario_publico.html", {
        "link": link,
        "sucesso": sucesso,
        "download_url": download_url,
        "campos": campos,
    })


def _placeholder_para_label(placeholder: str) -> str:
    return placeholder.replace("_", " ").title()


def _inferir_tipo_placeholder(placeholder: str) -> str:
    nome = placeholder.upper()
    if "DATA" in nome:
        return CampoTemplate.TIPO_DATE
    if "VALOR" in nome or "PRECO" in nome:
        return CampoTemplate.TIPO_CURRENCY
    if "EMAIL" in nome:
        return CampoTemplate.TIPO_EMAIL
    if "TELEFONE" in nome or "CELULAR" in nome:
        return CampoTemplate.TIPO_PHONE
    if "OBSERVAC" in nome or "OBSERV" in nome:
        return CampoTemplate.TIPO_TEXTAREA
    return CampoTemplate.TIPO_TEXT


def _placeholder_obrigatorio(placeholder: str) -> bool:
    opcionais = {"OBSERVACOES", "OBSERVACAO", "LOCAL_EVENTO"}
    return placeholder.upper() not in opcionais


def _parse_opcoes(raw: str) -> list[str] | None:
    if not raw:
        return None
    opcoes = [item.strip() for item in raw.split(",") if item.strip()]
    return opcoes or None


