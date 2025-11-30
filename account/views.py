from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    PCDRegistrationForm, 
    CompanyRegistrationForm, 
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm
)
from .services import (
    register_pcd_user, 
    register_company_user, 
    login_user,
    send_password_reset_email,
    validate_reset_token,
    reset_user_password
)
from .models import User


class RegisterChoiceView(View):
    
    template_name = "account/register_choice.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("account:panel")
        return render(request, self.template_name)


class RegisterPCDView(View):
    
    template_name = "account/register_pcd.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("account:panel")
        return render(request, self.template_name, {"form": PCDRegistrationForm()})
    
    def post(self, request):
        form = PCDRegistrationForm(request.POST)
        
        if form.is_valid():
            result = register_pcd_user(request, form)
            if result:
                return result
        
        return render(request, self.template_name, {"form": form})


class RegisterCompanyView(View):
    
    template_name = "account/register_company.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("account:panel")
        return render(request, self.template_name, {"form": CompanyRegistrationForm()})
    
    def post(self, request):
        form = CompanyRegistrationForm(request.POST)
        
        if form.is_valid():
            result = register_company_user(request, form)
            if result:
                return result
        
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    
    template_name = "account/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect("admin:index")
            return redirect("account:panel")
        
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            result = login_user(request, form.user)
            if result:
                return result
        
        return render(request, self.template_name, {"form": form})


class PanelView(LoginRequiredMixin, View):
    
    template_name = "account/panel.html"
    login_url = "account:login"
    
    def get(self, request):
        context = {
            "user": request.user,
            "tipo": request.user.tipo
        }
        return render(request, self.template_name, context)


class CustomLogoutView(LoginRequiredMixin, View):
    
    login_url = "account:login"
    
    def get(self, request):
        logout(request)
        messages.info(request, "Você saiu da sua conta. Até logo!")
        return redirect("account:login")
    
    def post(self, request):
        return self.get(request)


class CustomPasswordResetView(View):
    
    template_name = "account/forgot_password.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("account:panel")
        return render(request, self.template_name, {"form": PasswordResetRequestForm()})
    
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)
            
            if send_password_reset_email(request, user):
                return redirect("forgot_password_done")
        
        return render(request, self.template_name, {"form": form})
    
    @staticmethod
    def done_view(request):
        return render(request, "account/forgot_password_done.html")
    
    @staticmethod
    def confirm_view(request, uidb64, token):
        if request.method == "GET":
            user = validate_reset_token(uidb64, token)
            
            if not user:
                messages.error(request, "Link inválido ou expirado.")
                return redirect("forgot_password")
            
            return render(request, "account/password_reset_confirm.html", {
                "form": PasswordResetConfirmForm(),
                "uidb64": uidb64,
                "token": token
            })
        
        elif request.method == "POST":
            user = validate_reset_token(uidb64, token)
            
            if not user:
                messages.error(request, "Link inválido ou expirado.")
                return redirect("forgot_password")
            
            form = PasswordResetConfirmForm(request.POST)
            
            if form.is_valid():
                if reset_user_password(user, form.cleaned_data["password1"]):
                    messages.success(request, "Senha alterada com sucesso!")
                    return redirect("password_reset_complete")
                else:
                    messages.error(request, "Erro ao alterar senha. Tente novamente.")
            
            return render(request, "account/password_reset_confirm.html", {
                "form": form,
                "uidb64": uidb64,
                "token": token
            })
    
    @staticmethod
    def complete_view(request):
        return render(request, "account/password_reset_complete.html")