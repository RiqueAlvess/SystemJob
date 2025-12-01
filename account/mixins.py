from django import forms

class PasswordValidationMixin:
    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError("As senhas não coincidem")
            if len(p1) < 8:
                raise forms.ValidationError("A senha deve ter no mínimo 8 caracteres")
        
        return p2