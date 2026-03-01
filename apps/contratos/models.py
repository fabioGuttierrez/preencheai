import uuid
from django.db import models
from apps.core.models import Organizacao, Usuario
from apps.clientes.models import Cliente


class ModeloContrato(models.Model):
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE,
        related_name="modelos_contrato",
    )
    nome = models.CharField(max_length=255)
    arquivo_docx = models.FileField(upload_to="modelos/")
    supabase_path = models.CharField(max_length=500, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modelo de Contrato"
        verbose_name_plural = "Modelos de Contrato"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} ({self.organizacao.nome})"


class CampoTemplate(models.Model):
    TIPO_TEXT = "text"
    TIPO_TEXTAREA = "textarea"
    TIPO_DATE = "date"
    TIPO_DATETIME = "datetime"
    TIPO_NUMBER = "number"
    TIPO_CURRENCY = "currency"
    TIPO_EMAIL = "email"
    TIPO_PHONE = "phone"
    TIPO_SELECT = "select"
    TIPO_MULTISELECT = "multiselect"

    TIPOS = (
        (TIPO_TEXT, "Texto"),
        (TIPO_TEXTAREA, "Texto longo"),
        (TIPO_DATE, "Data"),
        (TIPO_DATETIME, "Data e hora"),
        (TIPO_NUMBER, "Numero"),
        (TIPO_CURRENCY, "Moeda"),
        (TIPO_EMAIL, "Email"),
        (TIPO_PHONE, "Telefone"),
        (TIPO_SELECT, "Selecao"),
        (TIPO_MULTISELECT, "Selecao multipla"),
    )

    modelo = models.ForeignKey(
        ModeloContrato,
        on_delete=models.CASCADE,
        related_name="campos",
    )
    placeholder = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    tipo = models.CharField(max_length=30, choices=TIPOS, default=TIPO_TEXT)
    obrigatorio = models.BooleanField(default=True)
    mascara = models.CharField(max_length=100, blank=True)
    ajuda = models.CharField(max_length=255, blank=True)
    opcoes = models.JSONField(null=True, blank=True)
    data_extenso = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Campo de Template"
        verbose_name_plural = "Campos de Template"
        ordering = ["ordem", "criado_em"]
        unique_together = ("modelo", "placeholder")

    def __str__(self):
        return f"{self.placeholder} ({self.modelo.nome})"


class Contrato(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE,
        related_name="contratos",
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="contratos",
    )
    modelo = models.ForeignKey(
        ModeloContrato,
        on_delete=models.SET_NULL,
        null=True,
        related_name="contratos",
    )
    arquivo_docx = models.FileField(upload_to="contratos/", blank=True)
    supabase_url = models.URLField(max_length=1000, blank=True)
    arquivo_pdf = models.FileField(upload_to="contratos/pdf/", blank=True)
    supabase_pdf_url = models.URLField(max_length=1000, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Contrato {self.id} - {self.cliente.nome}"


class ContratoEvento(models.Model):
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name="eventos",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_contrato",
    )
    acao = models.CharField(max_length=50)
    detalhes = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de Contrato"
        verbose_name_plural = "Eventos de Contrato"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.acao} ({self.contrato_id})"
