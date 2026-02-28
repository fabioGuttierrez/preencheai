from rest_framework import serializers
from .models import LinkFormulario
from apps.clientes.serializers import ClienteSerializer
from apps.contratos.serializers import ModeloContratoSerializer


class LinkFormularioSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.UUIDField(write_only=True)
    modelo = ModeloContratoSerializer(read_only=True)
    modelo_id = serializers.IntegerField(write_only=True)
    link_url = serializers.SerializerMethodField()

    class Meta:
        model = LinkFormulario
        fields = [
            "id", "token", "cliente", "cliente_id",
            "modelo", "modelo_id", "utilizado", "link_url", "criado_em",
        ]
        read_only_fields = ["id", "token", "utilizado", "criado_em"]

    def get_link_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/formulario/{obj.token}/")
        return f"/formulario/{obj.token}/"

    def validate_cliente_id(self, value):
        org = self.context["request"].user.organizacao
        from apps.clientes.models import Cliente
        if not Cliente.objects.filter(pk=value, organizacao=org).exists():
            raise serializers.ValidationError("Cliente não encontrado.")
        return value

    def validate_modelo_id(self, value):
        org = self.context["request"].user.organizacao
        from apps.contratos.models import ModeloContrato
        if not ModeloContrato.objects.filter(pk=value, organizacao=org, ativo=True).exists():
            raise serializers.ValidationError("Modelo não encontrado.")
        return value

    def create(self, validated_data):
        org = self.context["request"].user.organizacao
        from apps.clientes.models import Cliente
        from apps.contratos.models import ModeloContrato
        cliente = Cliente.objects.get(pk=validated_data.pop("cliente_id"), organizacao=org)
        modelo = ModeloContrato.objects.get(pk=validated_data.pop("modelo_id"), organizacao=org)
        return LinkFormulario.objects.create(
            organizacao=org,
            cliente=cliente,
            modelo=modelo,
            **validated_data,
        )


class DadosFormularioSerializer(serializers.Serializer):
    tipo_evento = serializers.CharField(max_length=255)
    data_evento = serializers.CharField(max_length=100)
    valor_total = serializers.CharField(max_length=50)
    local_evento = serializers.CharField(max_length=255, required=False, allow_blank=True)
    observacoes = serializers.CharField(required=False, allow_blank=True)
