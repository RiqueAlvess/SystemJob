from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.template.loader import render_to_string
import resend
from .models import User, PerfilPCD, PerfilEmpresa


resend.api_key = settings.API_RESEND


def register_pcd_user(request, form):
    try:
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password1"])
        user.is_active = True
        user.save()
     
        PerfilPCD.objects.create(
            user=user,
            cpf=form.cleaned_data.get("cpf", "")
        )
    
        login(request, user)
        user.ultima_sessao = timezone.now()
        user.save(update_fields=["ultima_sessao"])
        
        messages.success(
            request,
            f"Bem-vindo à Plataforma PCD, {user.nome_completo.split()[0]}! 🎉"
        )
        return redirect("account:panel")
        
    except Exception as e:
        messages.error(request, f"Erro ao criar conta: {str(e)}")
        return None


def register_company_user(request, form):
    try:
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password1"])
        user.is_active = True
        user.save()
  
        PerfilEmpresa.objects.create(
            user=user,
            cnpj=form.cleaned_data.get("cnpj", ""),
            razao_social=form.cleaned_data.get("razao_social", ""),
            telefone_principal=form.cleaned_data.get("telefone", "")
        )

        login(request, user)
        user.ultima_sessao = timezone.now()
        user.save(update_fields=["ultima_sessao"])
        
        messages.success(
            request,
            f"Bem-vindo à Plataforma PCD, {user.nome_completo.split()[0]}! 🎉"
        )
        return redirect("account:panel")
        
    except Exception as e:
        messages.error(request, f"Erro ao criar conta: {str(e)}")
        return None


def login_user(request, user):
    try:
        login(request, user)
        user.ultima_sessao = timezone.now()
        user.save(update_fields=["ultima_sessao"])
        
        messages.success(
            request,
            f"Bem-vindo de volta, {user.nome_completo.split()[0]}! 👋"
        )
   
        if user.is_staff or user.is_superuser:
            return redirect("admin:index")
        
        return redirect("account:panel")
        
    except Exception as e:
        messages.error(request, f"Erro ao fazer login: {str(e)}")
        return None


def send_password_reset_email(request, user):
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        
        context = {
            'user': user,
            'protocol': protocol,
            'domain': domain,
            'uid': uid,
            'token': token,
        }
        
        html_content = render_to_string('account/password_reset_email.html', context)
        
        params = {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": "Redefinição de senha - Plataforma PCD",
            "html": html_content,
        }
        
        resend.Emails.send(params)
        
        messages.success(
            request,
            "E-mail de redefinição enviado! Verifique sua caixa de entrada."
        )
        return True
        
    except Exception as e:
        messages.error(request, f"Erro ao enviar e-mail: {str(e)}")
        return False


def validate_reset_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            return user
        
        return None
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def reset_user_password(user, new_password):
    try:
        user.set_password(new_password)
        user.save()
        return True
        
    except Exception:
        return False