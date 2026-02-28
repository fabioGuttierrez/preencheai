from django.urls import path
from . import views

urlpatterns = [
    path("links/", views.links_list, name="links-list"),
    path("formulario/<uuid:token>/info/", views.formulario_info, name="formulario-info"),
    path("formulario/<uuid:token>/submit/", views.receber_formulario, name="formulario-submit"),
]
