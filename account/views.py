from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PCDRegistrationForm, CompanyRegistrationForm, LoginForm
from .services import register_pcd_user, register_company_user, login_user

class RegisterChoiceView(View):
    template_name = "account/register_choice.html"
    def get(self, request):
        return render(request, self.template_name)

class RegisterPCDView(View):
    template_name = "account/register_pcd.html"
    def get(self, request):
        return render(request, self.template_name, {"form": PCDRegistrationForm()})
    def post(self, request):
        form = PCDRegistrationForm(request.POST)
        if form.is_valid():
            return register_pcd_user(request, form)
        return render(request, self.template_name, {"form": form})

class RegisterCompanyView(View):
    template_name = "account/register_company.html"
    def get(self, request):
        return render(request, self.template_name, {"form": CompanyRegistrationForm()})
    def post(self, request):
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            return register_company_user(request, form)
        return render(request, self.template_name, {"form": form})

class LoginView(View):
    template_name = "account/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("admin:index") if request.user.is_staff else redirect("panel")
        return render(request, self.template_name)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            return login_user(request, form.user)
        messages.error(request, "E-mail ou senha incorretos.")
        return render(request, self.template_name, {"form": form})

class PanelView(LoginRequiredMixin, View):
    template_name = "account/panel.html"
    def get(self, request):
        return render(request, self.template_name, {"user": request.user, "tipo": request.user.tipo})

from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    next_page = "account:login"