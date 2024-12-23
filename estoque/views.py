# estoque/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .models import Equipamento, HistoricoEquipamento
from .forms import EquipamentoForm, EquipamentoBuscaForm
from django.core.paginator import Paginator
from django.http import HttpResponse 
import csv
from django.contrib import messages
from django.contrib.auth import authenticate, login 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User, Group


def home(request):
    return redirect('login')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {username}!')
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})



class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        group = Group.objects.get(name='Leitor')
        user.groups.add(group)
        messages.success(self.request, 'Conta criada com sucesso! Permissão de leitura atribuída.')
        return response

@login_required
@permission_required('estoque.view_equipamento', raise_exception=True)
def lista_equipamentos(request):
    form = EquipamentoBuscaForm(request.GET)
    equipamentos_list = Equipamento.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            equipamentos_list = equipamentos_list.filter(nome__icontains=query)

        setor = form.cleaned_data.get('setor')
        if setor:
            equipamentos_list = equipamentos_list.filter(setor__icontains=setor)

        tombamento = form.cleaned_data.get('tombamento')
        if tombamento:
            equipamentos_list = equipamentos_list.filter(tombamento__icontains(tombamento))

        categoria = form.cleaned_data.get('categoria')
        if categoria:
            equipamentos_list = equipamentos_list.filter(categoria=categoria)

    paginator = Paginator(equipamentos_list, 10)  # Mostrar 10 equipamentos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'estoque/lista_equipamentos.html', {
        'form': form,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'setor': form.cleaned_data.get('setor', ''),
        'tombamento': form.cleaned_data.get('tombamento', ''),
        'categoria': form.cleaned_data.get('categoria', ''),
    })


@login_required
@permission_required('estoque.view_equipamento', raise_exception=True)
def detalhe_equipamento(request, equipamento_id):
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    historicos = equipamento.historicos.all().order_by('-data_alteracao')
    return render(request, 'estoque/detalhe_equipamento.html', {'equipamento': equipamento, 'historicos': historicos})


@login_required
@permission_required('estoque.add_equipamento', raise_exception=True)
def criar_equipamento(request):
    if not request.user.has_perm('estoque.add_equipamento'):
        messages.error(request, 'Você não tem permissão para criar equipamentos.')
        return redirect('lista_equipamentos')

    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            equipamento = form.save()
            HistoricoEquipamento.objects.create(
                equipamento=equipamento,
                alterado_por=request.user,
                alteracao_tipo='Criação',
                descricao=f"Equipamento criado e cadastrado no setor {equipamento.setor}"
            )
            messages.success(request, 'Equipamento criado com sucesso!')
            return redirect('lista_equipamentos')
    else:
        form = EquipamentoForm()
    return render(request, 'estoque/criar_equipamento.html', {'form': form})



@login_required
def editar_equipamento(request, equipamento_id):
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    if not request.user.has_perm('estoque.change_equipamento'):
        messages.error(request, 'Você não tem permissão para editar equipamentos.')
        return redirect('detalhe_equipamento', equipamento_id=equipamento_id)

    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            equipamento_atual = form.save(commit=False)
            descricao = []
            if equipamento.setor != equipamento_atual.setor:
                descricao.append(f"Setor alterado de {equipamento.setor} para {equipamento_atual.setor}")
            if equipamento.status != equipamento_atual.status:
                descricao.append(f"Status alterado de {equipamento.status} para {equipamento_atual.status}")
            if descricao:
                HistoricoEquipamento.objects.create(
                    equipamento=equipamento_atual,
                    alterado_por=request.user,
                    alteracao_tipo='Alteração',
                    descricao="; ".join(descricao)
                )
            equipamento_atual.save()
            messages.success(request, 'Equipamento editado com sucesso!')
            return redirect('detalhe_equipamento', equipamento_id=equipamento.id)
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'estoque/editar_equipamento.html', {'form': form})



@login_required
def deletar_equipamento(request, equipamento_id):
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    if not request.user.has_perm('estoque.delete_equipamento'):
        messages.error(request, 'Você não tem permissão para excluir equipamentos.')
        return redirect('detalhe_equipamento', equipamento_id=equipamento_id)

    if request.method == 'POST':
        equipamento.delete()
        messages.success(request, 'Equipamento excluído com sucesso!')
        return redirect('lista_equipamentos')
    return render(request, 'estoque/confirmar_deletar_equipamento.html', {'equipamento': equipamento})

@login_required
@permission_required('estoque.view_equipamento', raise_exception=True)
def exportar_relatorio(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_equipamentos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nome', 'Status', 'Descrição', 'Criado em'])

    equipamentos = Equipamento.objects.all().values_list('nome', 'status', 'descricao', 'criado_em')
    for equipamento in equipamentos:
        writer.writerow(equipamento)
    return response


@login_required
@permission_required('auth.change_user', raise_exception=True)
def gerenciar_usuarios(request):
    usuarios = User.objects.all()
    grupos = Group.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        user = User.objects.get(id=user_id)
        group = Group.objects.get(id=group_id)
        user.groups.clear()
        user.groups.add(group)
        messages.success(request, f'Permissões atualizadas para o usuário {user.username}!')
        return redirect('gerenciar_usuarios')

    return render(request, 'registration/gerenciar_usuarios.html', {
        'usuarios': usuarios,
        'grupos': grupos,
    })

