from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from .models import Vaga, Candidatura
from .forms import VagaForm
from .services import (
    criar_vaga, submeter_para_aprovacao,
    candidatar_pcd, VagaPublicarView
)


class MinhasVagasListView(LoginRequiredMixin, View):
    template_name = "job_vacancies/minhas_vagas.html"

    def get(self, request):
        if request.user.tipo != 'empresa':
            messages.error(request, "Acesso restrito a empresas.")
            return redirect("account:panel")

        vagas = Vaga.objects.filter(empresa=request.user).order_by('-criado_em')
        return render(request, self.template_name, {"vagas": vagas})


class VagaCreateView(LoginRequiredMixin, View):
    template_name = "job_vacancies/vaga_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": VagaForm(), "title": "Nova Vaga"})

    def post(self, request):
        form = VagaForm(request.POST)
        if form.is_valid():
            vaga = criar_vaga(request.user, form.cleaned_data)
            messages.success(request, "Vaga criada como rascunho!", extra_tags="success")
            return redirect("job_vacancies:vaga_detail", vaga.pk)
        return render(request, self.template_name, {"form": form, "title": "Nova Vaga"})


class VagaDetailView(LoginRequiredMixin, View):
    template_name = "job_vacancies/vaga_detail.html"

    def get(self, request, pk):
        vaga = get_object_or_404(Vaga, pk=pk)

        if request.user.tipo == 'empresa' and vaga.empresa != request.user:
            messages.error(request, "Você não autorizado.")
            return redirect("account:panel")

        candidaturas = vaga.candidaturas.select_related('pcd').prefetch_related('pcd__perfil_pcd__deficiencias') if request.user.tipo == 'empresa' else None

        return render(request, self.template_name, {
            "vaga": vaga,
            "candidaturas": candidaturas,
            "pode_editar": vaga.pode_ser_editada(),
        })


class VagaSubmeterAprovacaoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        vaga = get_object_or_404(Vaga, pk=pk, empresa=request.user)
        try:
            submeter_para_aprovacao(vaga, request.user)
            messages.success(request, "Vaga enviada para avaliação médica!")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("job_vacancies:vaga_detail", pk)


class VagaPublicarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        vaga = get_object_or_404(Vaga, pk=pk, empresa=request.user, status='aprovada')
        vaga.publicar()
        messages.success(request, "Vaga publicada com sucesso!")
        return redirect("job_vacancies:minhas_vagas")