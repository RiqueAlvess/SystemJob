from django import forms
from .models import User, PerfilPCD, PerfilEmpresa

class PCDRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full", "placeholder": "Mínimo 8 caracteres"})
    )
    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full", "placeholder": "Repita a senha"})
    )
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "000.000.000-00"})
    )

    class Meta:
        model = User
        fields = ["nome_completo", "email", "telefone"]
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Nome completo"}),
            "email": forms.EmailInput(attrs={"class": "input input-bordered w-full", "placeholder": "seu@email.com"}),
            "telefone": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "(00) 00000-0000"}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas não coincidem")
        if len(p1) < 8:
            raise forms.ValidationError("A senha deve ter no mínimo 8 caracteres")
        return p2

class CompanyRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full"})
    )
    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full"})
    )
    cnpj = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "00.000.000/0000-00"})
    )

    class Meta:
        model = User
        fields = ["nome_completo", "email"]
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "Nome do responsável"}),
            "email": forms.EmailInput(attrs={"class": "input input-bordered w-full", "placeholder": "empresa@dominio.com"}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("As senhas não coincidem")
        if len(p1) < 8:
            raise forms.ValidationError("A senha deve ter no mínimo 8 caracteres")
        return p2

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input input-bordered w-full", "placeholder": "seu@email.com", "autofocus": True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input input-bordered w-full", "placeholder": "••••••••"})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("E-mail ou senha incorretos")
            if not user.is_active:
                raise forms.ValidationError("Esta conta está desativada")
            self.user = user
        return cleaned_data