# estoque/models.py

from django.db import models
from django.contrib.auth.models import User

CATEGORIAS = [
    ('Computadores', 'Computadores'),
    ('Monitores', 'Monitores'),
    ('Raspberry', 'Raspberry'),
    ('Impressoras', 'Impressoras'),
    ('Notebooks', 'Notebooks'),
    ('Outros', 'Outros'),
]

class Equipamento(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    tombamento = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    setor = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class HistoricoEquipamento(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='historicos')
    alterado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    alteracao_tipo = models.CharField(max_length=50)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField()

    def __str__(self):
        return f"{self.equipamento.nome} - {self.alteracao_tipo} em {self.data_alteracao}"
