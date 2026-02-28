import uuid
from django.db import models
from apps.core.models import Organizacao
from apps.clientes.models import Cliente
from apps.contratos.models import ModeloContrato


class LinkFormulario(models.Model):
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE,
        related_name="links_formulario",
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="links_formulario",
    )
    modelo = models.ForeignKey(
        ModeloContrato,
        on_delete=models.CASCADE,
        related_name="links_formulario",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    utilizado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Link de Formulário"
        verbose_name_plural = "Links de Formulário"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Link {self.token} - {self.cliente.nome}"
