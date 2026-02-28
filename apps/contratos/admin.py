from django.contrib import admin
from .models import ModeloContrato, Contrato, CampoTemplate, ContratoEvento


@admin.register(ModeloContrato)
class ModeloContratoAdmin(admin.ModelAdmin):
    list_display = ("nome", "organizacao", "ativo", "criado_em")
    list_filter = ("organizacao", "ativo")
    search_fields = ("nome",)


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "modelo", "organizacao", "criado_em")
    list_filter = ("organizacao",)
    search_fields = ("cliente__nome",)


@admin.register(CampoTemplate)
class CampoTemplateAdmin(admin.ModelAdmin):
    list_display = ("placeholder", "label", "tipo", "obrigatorio", "modelo", "ordem", "ativo")
    list_filter = ("modelo", "tipo", "obrigatorio", "ativo")
    search_fields = ("placeholder", "label", "modelo__nome")


@admin.register(ContratoEvento)
class ContratoEventoAdmin(admin.ModelAdmin):
    list_display = ("acao", "contrato", "usuario", "criado_em")
    list_filter = ("acao", "criado_em")
    search_fields = ("contrato__id", "usuario__username")
