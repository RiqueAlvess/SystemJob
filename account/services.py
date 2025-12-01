from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.template.loader import render_to_string
from django.db import transaction
import resend
import logging
from .models import User, PerfilPCD, PerfilEmpresa
from .constants import Messages
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

resend.api_key = settings.API_RESEND

def register_doctor_user(form):
    doctor_group, _= Group.objects.get_or_create(name='Médico')
    User.groups.add(doctor_group)

def update_user_metadata(user, request=None, update_session=False):
    if request and request.user.is_authenticated:
        if not user.pk:
            user.criado_por = request.user
        user.modificado_por = request.user
    
    if update_session:
        user.ultima_sessao = timezone.now()
    
    user.save()
    return user


def register_pcd_user(form):
    
    try:
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.is_active = True
            update_user_metadata(user)
            
            PerfilPCD.objects.create(
                user=user,
                cpf=form.cleaned_data.get("cpf", ""),
                data_nascimento=form.cleaned_data.get("data_nascimento")
            )
            
            return (True, user, None)
            
    except Exception as e:
        error_message = f"Erro ao registrar usuário PCD: {str(e)}"
        logger.error(error_message, exc_info=True)
        return (False, None, error_message)

def register_company_user(form):
    
    try:
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.is_active = False
            update_user_metadata(user)
  
            PerfilEmpresa.objects.create(
                user=user,
                cnpj=form.cleaned_data.get("cnpj", ""),
                razao_social=form.cleaned_data.get("nome_completo", ""),
                telefone_principal=form.cleaned_data.get("telefone", "")
            )

            return (True, user, None)
            
    except Exception as e:
        error_message = f"Erro ao registrar usuário Empresa: {str(e)}"
        logger.error(error_message, exc_info=True)
        return (False, None, error_message)


def login_user(request, user):
    login(request, user)
    update_user_metadata(user, update_session=True)
    messages.success(
        request,
        Messages.LOGIN_SUCCESS.format(user.primeiro_nome)
    )


def send_password_reset_email(request, user):
    if not user.is_active:
        return False

    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
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
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de reset: {str(e)}", exc_info=True)
        return False


def validate_reset_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token) and user.is_active:
            return user
        
        return None
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def reset_user_password(user, new_password):
    try:
        user.set_password(new_password)
        update_user_metadata(user)
        return True
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {str(e)}", exc_info=True)
        return False