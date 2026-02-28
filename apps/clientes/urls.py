from django.urls import path
from . import views

urlpatterns = [
    path("clientes/", views.clientes_list, name="clientes-list"),
    path("clientes/<uuid:pk>/", views.cliente_detail, name="cliente-detail"),
]
