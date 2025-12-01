from django import forms
from .models import Vaga, RecursoAcessibilidade


class VagaForm(forms.ModelForm):
    recursos_disponiveis = forms.ModelMultipleChoiceField(
        queryset=RecursoAcessibilidade.objects.all().order_by('nome'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Recursos de Acessibilidade Disponíveis na Empresa"
    )

    class Meta:
        model = Vaga
        fields = [
            'titulo', 'descricao', 'tipo', 'modalidade', 'localizacao',
            'salario_min', 'salario_max', 'mostrar_salario',
            'recursos_disponiveis'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Descreva a vaga, responsabilidades, requisitos e cultura da empresa...'}),
            'tipo': forms.RadioSelect(choices=Vaga.TIPO_CHOICES),
            'modalidade': forms.RadioSelect,
            'salario_min': forms.NumberInput(attrs={'step': '100.00', 'placeholder': '4.000,00'}),
            'salario_max': forms.NumberInput(attrs={'step': '100.00', 'placeholder': '7.000,00'}),
        }
        labels = {
            'titulo': 'Título da Vaga',
            'tipo': 'Tipo de Oportunidade',
            'modalidade': 'Modalidade de Trabalho',
            'localizacao': 'Cidade/Estado (ou "100% Remoto")',
            'mostrar_salario': 'Mostrar faixa salarial publicamente?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].widget.attrs.update({'class': 'input-lg', 'placeholder': 'Ex: Desenvolvedor Backend Pleno'})
        self.fields['localizacao'].widget.attrs.update({'placeholder': 'São Paulo/SP ou Remoto'})