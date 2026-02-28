from rest_framework import serializers
from .models import Organizacao, Usuario


class OrganizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacao
        fields = ["id", "nome", "cnpj", "criado_em"]
        read_only_fields = ["id", "criado_em"]


class UsuarioSerializer(serializers.ModelSerializer):
    organizacao = OrganizacaoSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "first_name", "last_name", "organizacao"]
        read_only_fields = ["id"]


class RegistroSerializer(serializers.Serializer):
    nome_organizacao = serializers.CharField(max_length=255)
    cnpj = serializers.CharField(max_length=18, required=False, allow_blank=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username já em uso.")
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("E-mail já cadastrado.")
        return value

    def create(self, validated_data):
        org = Organizacao.objects.create(
            nome=validated_data["nome_organizacao"],
            cnpj=validated_data.get("cnpj", ""),
        )
        user = Usuario.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            organizacao=org,
        )
        return user
