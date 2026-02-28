from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nome", "cpf", "email", "telefone", "criado_em"]
        read_only_fields = ["id", "criado_em"]

    def create(self, validated_data):
        organizacao = self.context["request"].user.organizacao
        return Cliente.objects.create(organizacao=organizacao, **validated_data)
