from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ModeloContrato, Contrato
from .serializers import ModeloContratoSerializer, ContratoSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def modelos_list(request):
    org = request.user.organizacao

    if request.method == "GET":
        modelos = ModeloContrato.objects.filter(organizacao=org, ativo=True)
        serializer = ModeloContratoSerializer(modelos, many=True)
        return Response(serializer.data)

    serializer = ModeloContratoSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def modelo_detail(request, pk):
    org = request.user.organizacao
    modelo = get_object_or_404(ModeloContrato, pk=pk, organizacao=org)

    if request.method == "GET":
        return Response(ModeloContratoSerializer(modelo).data)

    modelo.ativo = False
    modelo.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def contratos_list(request):
    org = request.user.organizacao
    contratos = Contrato.objects.filter(organizacao=org).select_related("cliente", "modelo")
    serializer = ContratoSerializer(contratos, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def contrato_detail(request, pk):
    org = request.user.organizacao
    contrato = get_object_or_404(Contrato, pk=pk, organizacao=org)
    return Response(ContratoSerializer(contrato, context={"request": request}).data)
