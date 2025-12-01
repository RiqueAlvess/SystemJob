from django import forms
from django.contrib.auth import authenticate
from .models import User, PerfilPCD, PerfilEmpresa
from .mixins import PasswordValidationMixin


class PCDRegistrationForm(PasswordValidationMixin, forms.ModelForm):
    
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Mínimo 8 caracteres"
        })
    )
    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Repita a senha"
        })
    )
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "000.000.000-00",
            "x-mask": "999.999.999-99"
        })
    )
    data_nascimento = forms.DateField(
        label="Data de Nascimento",
        widget=forms.DateInput(attrs={
            "class": "input input-bordered w-full",
            "type": "date"
        })
    )

    class Meta:
        model = User
        fields = ["nome_completo", "email", "telefone"]
        widgets = {
            "nome_completo": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Nome completo"
            }),
            "email": forms.EmailInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "seu@email.com"
            }),
            "telefone": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "(00) 00000-0000",
                "x-mask": "(99) 99999-9999"
            }),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        if PerfilPCD.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Este CPF já está cadastrado.")
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email


class CompanyRegistrationForm(PasswordValidationMixin, forms.ModelForm):
    
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Mínimo 8 caracteres"
        })
    )
    password2 = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Repita a senha"
        })
    )
    cnpj = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "00.000.000/0000-00",
            "x-mask": "99.999.999/9999-99"
        })
    )

    class Meta:
        model = User
        fields = ["nome_completo", "email"]
        widgets = {
            "nome_completo": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Nome completo do responsável"
            }),
            "email": forms.EmailInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "seu@email.com"
            }),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")
        if PerfilEmpresa.objects.filter(cnpj=cnpj).exists():
            raise forms.ValidationError("Este CNPJ já está cadastrado.")
        return cnpj

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "seu@email.com",
            "autofocus": True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "••••••••"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("E-mail ou senha inválidos.")
            
            if not user.is_active:
                raise forms.ValidationError("Conta desativada")
            
            self.user = user
        
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "seu@email.com",
            "autofocus": True
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Não existe uma conta com este e-mail.")
        
        return email


class PasswordResetConfirmForm(PasswordValidationMixin, forms.Form):
    
    password1 = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Mínimo 8 caracteres"
        })
    )
    password2 = forms.CharField(
        label="Confirme a Senha",
        widget=forms.PasswordInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Repita a senha"
        })
    )