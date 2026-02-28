from rest_framework import serializers
from .models import ModeloContrato, Contrato
from apps.clientes.serializers import ClienteSerializer


class ModeloContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeloContrato
        fields = ["id", "nome", "arquivo_docx", "ativo", "criado_em"]
        read_only_fields = ["id", "criado_em"]

    def create(self, validated_data):
        organizacao = self.context["request"].user.organizacao
        return ModeloContrato.objects.create(organizacao=organizacao, **validated_data)


class ContratoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    modelo_nome = serializers.CharField(source="modelo.nome", read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Contrato
        fields = [
            "id",
            "cliente",
            "modelo_nome",
            "supabase_url",
            "supabase_pdf_url",
            "download_url",
            "criado_em",
        ]
        read_only_fields = ["id", "criado_em"]

    def get_download_url(self, obj):
        if obj.supabase_pdf_url:
            return obj.supabase_pdf_url
        if obj.arquivo_pdf:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.arquivo_pdf.url)
        if obj.supabase_url:
            return obj.supabase_url
        if obj.arquivo_docx:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.arquivo_docx.url)
        return None
