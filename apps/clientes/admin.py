from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "organizacao", "criado_em")
    list_filter = ("organizacao",)
    search_fields = ("nome", "telefone")
