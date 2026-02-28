from django.urls import path
from . import views

urlpatterns = [
    path("modelos/", views.modelos_list, name="modelos-list"),
    path("modelos/<int:pk>/", views.modelo_detail, name="modelo-detail"),
    path("contratos/", views.contratos_list, name="contratos-list"),
    path("contratos/<uuid:pk>/", views.contrato_detail, name="contrato-detail"),
]
