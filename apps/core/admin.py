from django.contrib import admin
from .models import Organizacao, Usuario


@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "criado_em")
    search_fields = ("nome", "cnpj")


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "organizacao", "is_staff")
    list_filter = ("organizacao",)
    search_fields = ("username", "email")
