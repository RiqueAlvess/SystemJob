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
from .constants import Routes, Messages


class RegisterChoiceView(View):
    
    template_name = "account/register_choice.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(Routes.ACCOUNT_PANEL)
        return render(request, self.template_name)


class RegisterPCDView(View):
    
    template_name = "account/register_pcd.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(Routes.ACCOUNT_PANEL)
        return render(request, self.template_name, {"form": PCDRegistrationForm()})
    
    def post(self, request):
        form = PCDRegistrationForm(request.POST)
        
        if form.is_valid():
            success, user, error = register_pcd_user(form)
            
            if success:
                login_user(request, user)
                messages.success(
                    request, 
                    Messages.REGISTER_PCD_SUCCESS.format(user.primeiro_nome)
                )
                return redirect(Routes.ACCOUNT_PANEL)
            else:
                messages.error(request, error)

        return render(request, self.template_name, {"form": form})


class RegisterCompanyView(View):
    
    template_name = "account/register_company.html"
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(Routes.ACCOUNT_PANEL)
        return render(request, self.template_name, {"form": CompanyRegistrationForm()})
    
    def post(self, request):
        form = CompanyRegistrationForm(request.POST)
        
        if form.is_valid():
            success, user, error = register_company_user(form)
            
            if success:
                messages.success(
                    request, 
                    Messages.REGISTER_COMPANY_SUCCESS.format(user.primeiro_nome)
                )
                return redirect(Routes.ACCOUNT_LOGIN)
            else:
                messages.error(request, error)
        
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    
    template_name = "account/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect(Routes.ADMIN_INDEX)
            return redirect(Routes.ACCOUNT_PANEL)
        return render(request, self.template_name, {"form": LoginForm()})
    
    def post(self, request):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.user
            login_user(request, user)
            
            if user.is_staff:
                return redirect(Routes.ADMIN_INDEX)
            return redirect(Routes.ACCOUNT_PANEL)
        
        return render(request, self.template_name, {"form": form})


class CustomLogoutView(View):
    
    def get(self, request):
        messages.info(request, Messages.LOGOUT_INFO)
        logout(request)
        return redirect(Routes.ACCOUNT_LOGIN)


class PanelView(LoginRequiredMixin, View):
    
    template_name = "account/panel.html"
    
    def get(self, request):
        user = request.user
        context = {
            "user": user,
            "primeiro_nome": user.primeiro_nome,
            "tipo": user.tipo,
        }
        return render(request, self.template_name, context)


class PasswordResetView:
    
    @staticmethod
    def request_view(request):
        if request.method == "POST":
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                try:
                    user = User.objects.get(email=form.cleaned_data["email"])
                    send_password_reset_email(request, user)
                    messages.success(request, Messages.PASSWORD_RESET_EMAIL_SENT)
                except User.DoesNotExist:
                    messages.success(request, Messages.PASSWORD_RESET_EMAIL_SENT)  
                return redirect("account:password_reset_sent") 
        else:
            form = PasswordResetRequestForm()
        return render(request, "account/forgot_password.html", {"form": form})

    @staticmethod
    def confirm_view(request, uidb64, token):
        user = validate_reset_token(uidb64, token)
        if not user:
            messages.error(request, Messages.PASSWORD_RESET_INVALID_LINK)
            return redirect("account:forgot_password")

        if request.method == "POST":
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                if reset_user_password(user, form.cleaned_data["password1"]):
                    messages.success(request, Messages.PASSWORD_RESET_SUCCESS)
                    return redirect("account:password_reset_complete")
        else:
            form = PasswordResetConfirmForm()

        return render(request, "account/password_reset_confirm.html", {
            "form": form,
            "uidb64": uidb64,
            "token": token
        })

    @staticmethod
    def sent_view(request):
        return render(request, "account/password_reset_sent.html")
    
    @staticmethod
    def complete_view(request):
        return render(request, "account/password_reset_complete.html")
    