from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError
from account.models import User
from .models import Vaga, AvaliacaoVagaMedica, Candidatura, Conversa
from datetime import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import VagaForm


class VagaPublicarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        vaga = get_object_or_404(Vaga, pk=pk, empresa=request.user, status='aprovada')
        vaga.publicar()  
        messages.success(request, "Vaga publicada com sucesso!")
        return redirect("job_vacancies:minhas_vagas")


def criar_vaga(empresa_user: User, dados: dict) -> Vaga:
    if empresa_user.tipo != 'empresa':
        raise PermissionDenied("Apenas empresas podem criar vagas")

    with transaction.atomic():
        vaga = Vaga.objects.create(
            empresa=empresa_user,
            **dados
        )

        AvaliacaoVagaMedica.objects.create(vaga=vaga)
    return vaga


def submeter_para_aprovacao(vaga: Vaga, empresa_user: User):
    if vaga.empresa != empresa_user:
        raise PermissionDenied()
    if vaga.status != 'rascunho':
        raise ValidationError("Vaga já foi submetida ou publicada")

    vaga.status = 'aguardando_aprovacao'
    vaga.save(update_fields=['status'])


def aprovar_vaga_medico(vaga, medico_user, deficiencias_ids, observacoes="", ajustes="", status_avaliacao='aprovada'):
    if not medico_user.groups.filter(name='Médico').exists():
        raise PermissionDenied("Apenas médicos podem avaliar vagas")

    with transaction.atomic():

        avaliacao = vaga.avaliacoes_medicas.latest('id')
        avaliacao.medico = medico_user
        avaliacao.deficiencias_elegiveis.set(deficiencias_ids)
        avaliacao.status = status_avaliacao
        avaliacao.observacoes = observacoes
        avaliacao.ajustes_recomendados = ajustes
        avaliacao.avaliado_em = timezone.now()
        avaliacao.save()

        if status_avaliacao == 'aprovada':
            vaga.status = 'aprovada'
        elif status_avaliacao == 'rejeitada':
            vaga.status = 'rejeitada'
        elif status_avaliacao == 'ajustes_necessarios':
            vaga.status = 'ajustes_necessarios'

        vaga.save(update_fields=['status'])


def candidatar_pcd(pcd_user: User, vaga: Vaga, mensagem: str = ""):
    if pcd_user.tipo != 'pcd':
        raise PermissionDenied()

    if vaga.status != 'aberta':
        raise ValidationError("Vaga não está aberta")

    avaliacao = vaga.avaliacoes_medicas.filter(status='aprovada').latest('avaliado_em')
    deficiencias_pcd = set(pcd_user.perfil_pcd.deficiencias.values_list('id', flat=True))
    elegiveis = set(avaliacao.deficiencias_elegiveis.values_list('id', flat=True))

    if not deficiencias_pcd.intersection(elegiveis):
        raise ValidationError("Você não possui deficiência compatível com esta vaga")

    with transaction.atomic():
        candidatura, created = Candidatura.objects.get_or_create(
            vaga=vaga, pcd=pcd_user, defaults={'mensagem_candidato': mensagem}
        )
        if not created:
            raise ValidationError("Você já se candidatou a esta vaga")

        Conversa.objects.create(candidatura=candidatura)
   
    return candidatura