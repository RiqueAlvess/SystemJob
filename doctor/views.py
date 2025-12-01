from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Avg, F, Q, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta

from job_vacancies.models import Vaga, AvaliacaoVagaMedica
from job_vacancies.services import aprovar_vaga_medico
from account.models import CategoriaDeficiencia


class DoctorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Médico').exists():
            messages.error(request, "Acesso restrito a médicos.")
            return redirect("account:login")
        return super().dispatch(request, *args, **kwargs)


class DashboardDoctorView(DoctorRequiredMixin, LoginRequiredMixin, View):
    template_name = "doctor/dashboard.html"

    def get(self, request):
        hoje = timezone.now().date()
        ultimo_mes = hoje - timedelta(days=30)

        metricas = AvaliacaoVagaMedica.objects.filter(
            medico=request.user,
            avaliado_em__date__gte=ultimo_mes
        ).aggregate(
            total=Count('id'),
            aprovadas=Count('id', filter=Q(status='aprovada')),
            rejeitadas=Count('id', filter=Q(status='rejeitada')),
            ajustes=Count('id', filter=Q(status='ajustes_necessarios')),
            tempo_medio=Avg(
                ExpressionWrapper(F('avaliado_em') - F('vaga__criado_em'), output_field=DurationField())
            )
        )

        context = {
            "metricas": {
                "total": metricas['total'] or 0,
                "aprovadas": metricas['aprovadas'] or 0,
                "rejeitadas": metricas['rejeitadas'] or 0,
                "ajustes": metricas['ajustes'] or 0,
                "taxa_aprovacao": round((metricas['aprovadas'] or 0) / max(metricas['total'] or 1, 1) * 100, 1),
                "tempo_medio": metricas['tempo_medio'],
            },
            "vagas_pendentes": Vaga.objects.filter(status='aguardando_aprovacao').count(),
        }
        return render(request, self.template_name, context)


class FilaAprovacaoView(DoctorRequiredMixin, LoginRequiredMixin, View):
    template_name = "doctor/fila.html"

    def get(self, request):
        vagas = Vaga.objects.filter(
            status='aguardando_aprovacao'
        ).select_related('empresa').prefetch_related('recursos_disponiveis', 'avaliacoes_medicas')

        return render(request, self.template_name, {"vagas": vagas})


class AvaliarVagaView(DoctorRequiredMixin, LoginRequiredMixin, View):
    template_name = "doctor/avaliar_vaga.html"

    def get(self, request, pk):
        vaga = get_object_or_404(Vaga, pk=pk, status='aguardando_aprovacao')
        avaliacao = vaga.avaliacoes_medicas.filter(medico__isnull=True).first() or vaga.avaliacoes_medicas.latest('id')
        deficiencias = CategoriaDeficiencia.objects.all()

        return render(request, self.template_name, {
            "vaga": vaga,
            "avaliacao": avaliacao,
            "deficiencias": deficiencias,
        })

    def post(self, request, pk):
        vaga = get_object_or_404(Vaga, pk=pk, status='aguardando_aprovacao')
        deficiencias_ids = request.POST.getlist('deficiencias')
        status = request.POST.get('status')
        observacoes = request.POST.get('observacoes', '')
        ajustes = request.POST.get('ajustes', '')

        try:
            aprovar_vaga_medico(
                vaga=vaga,
                medico_user=request.user,
                deficiencias_ids=[int(d) for d in deficiencias_ids],
                observacoes=observacoes,
                ajustes=ajustes,
                status_avaliacao=status
            )
            messages.success(request, "Vaga avaliada com sucesso!")
            return redirect("doctor:fila")
        except Exception as e:
            messages.error(request, f"Erro ao avaliar: {e}")

        return redirect("doctor:fila")