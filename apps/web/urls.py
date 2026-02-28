from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("termos/", views.termos_view, name="termos"),
    path("privacidade/", views.privacidade_view, name="privacidade"),
    path("app/", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("logout/", views.logout_view, name="logout"),

    # Clientes
    path("clientes/", views.clientes_lista, name="clientes_lista"),
    path("clientes/novo/", views.cliente_criar, name="cliente_criar"),
    path("clientes/<uuid:pk>/editar/", views.cliente_editar, name="cliente_editar"),
    path("clientes/<uuid:pk>/deletar/", views.cliente_deletar, name="cliente_deletar"),

    # Modelos
    path("modelos/", views.modelos_lista, name="modelos_lista"),
    path("modelos/upload/", views.modelo_upload, name="modelo_upload"),
    path("modelos/<int:pk>/campos/", views.modelo_campos_config, name="modelo_campos_config"),
    path("modelos/<int:pk>/deletar/", views.modelo_deletar, name="modelo_deletar"),

    # Contratos
    path("contratos/", views.contratos_lista, name="contratos_lista"),

    # Links
    path("links/", views.links_lista, name="links_lista"),
    path("links/novo/", views.link_criar, name="link_criar"),
    path("links/<uuid:token>/", views.link_detalhe, name="link_detalhe"),

    # Formulário público
    path("formulario/<uuid:token>/", views.formulario_publico, name="formulario_publico"),
]
