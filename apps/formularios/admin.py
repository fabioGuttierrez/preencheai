from django.contrib import admin
from .models import LinkFormulario


@admin.register(LinkFormulario)
class LinkFormularioAdmin(admin.ModelAdmin):
    list_display = ("token", "cliente", "modelo", "utilizado", "organizacao", "criado_em")
    list_filter = ("organizacao", "utilizado")
    search_fields = ("cliente__nome", "token")
    readonly_fields = ("token",)
