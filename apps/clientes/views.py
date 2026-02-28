from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cliente
from .serializers import ClienteSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def clientes_list(request):
    org = request.user.organizacao

    if request.method == "GET":
        clientes = Cliente.objects.filter(organizacao=org)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    serializer = ClienteSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def cliente_detail(request, pk):
    org = request.user.organizacao
    cliente = get_object_or_404(Cliente, pk=pk, organizacao=org)

    if request.method == "GET":
        return Response(ClienteSerializer(cliente).data)

    if request.method == "PUT":
        serializer = ClienteSerializer(cliente, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    cliente.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
