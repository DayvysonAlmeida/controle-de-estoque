# estoque/urls.py

from django.urls import path
from .views import user_login, SignUpView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', user_login, name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('equipamentos/', views.lista_equipamentos, name='lista_equipamentos'),
    path('equipamentos/criar/', views.criar_equipamento, name='criar_equipamento'),
    path('equipamentos/<int:equipamento_id>/', views.detalhe_equipamento, name='detalhe_equipamento'),
    path('equipamentos/<int:equipamento_id>/editar/', views.editar_equipamento, name='editar_equipamento'),
    path('equipamentos/<int:equipamento_id>/deletar/', views.deletar_equipamento, name='deletar_equipamento'),
    path('relatorios/exportar/', views.exportar_relatorio, name='exportar_relatorio'),
    path('gerenciar_usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),  # URL de gerenciamento de usuários
]
