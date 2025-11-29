# account/services.py
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import User, PerfilPCD, PerfilEmpresa


def register_pcd_user(request, form):
    user = form.save(commit=False)
    user.set_password(form.cleaned_data["password1"])
    user.is_active = True
    user.save()
    PerfilPCD.objects.create(user=user, cpf=form.cleaned_data.get("cpf", ""))
    login(request, user)
    user.ultima_sessao = timezone.now()
    user.save(update_fields=["ultima_sessao"])
    messages.success(request, f"Bem-vindo, {user.nome_completo.split()[0]}!")
    return redirect("panel")


def register_company_user(request, form):
    user = form.save(commit=False)
    user.set_password(form.cleaned_data["password1"])
    user.is_active = True
    user.save()
    PerfilEmpresa.objects.create(
        user=user,
        cnpj=form.cleaned_data.get("cnpj", ""),
        razao_social=form.cleaned_data.get("nome_completo", "")
    )
    login(request, user)
    user.ultima_sessao = timezone.now()
    user.save(update_fields=["ultima_sessao"])
    messages.success(request, f"Bem-vindo, {user.nome_completo.split()[0]}!")
    return redirect("panel")


def login_user(request, user):
    login(request, user)
    user.ultima_sessao = timezone.now()
    user.save(update_fields=["ultima_sessao"])
    messages.success(request, f"Bem-vindo de volta, {user.nome_completo.split()[0]}!")
    if user.is_staff or user.is_superuser:
        return redirect("admin:index")
    return redirect("panel")