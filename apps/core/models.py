import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Organizacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"

    def __str__(self):
        return self.nome


class Usuario(AbstractUser):
    organizacao = models.ForeignKey(
        Organizacao,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.email
