from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import (
    RecursoAcessibilidade,
    Vaga,
    AvaliacaoVagaMedica,
    Candidatura,
    Conversa,
    Mensagem,
    CategoriaDeficiencia
)


@admin.register(CategoriaDeficiencia)
class CategoriaDeficienciaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'id']
    search_fields = ['nome']
    ordering = ['nome']


@admin.register(RecursoAcessibilidade)
class RecursoAcessibilidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone', 'id']
    search_fields = ['nome']
    list_editable = ['icone']
    ordering = ['nome']


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'empresa_link', 'status_badge', 'tipo', 'modalidade',
        'criado_em', 'visualizacoes', 'candidaturas_count'
    ]
    list_filter = ['status', 'tipo', 'modalidade', 'empresa', 'criado_em']
    search_fields = ['titulo', 'descricao', 'empresa__nome_completo', 'empresa__email']
    readonly_fields = ['visualizacoes', 'criado_em', 'atualizado_em', 'publicado_em']
    autocomplete_fields = ['empresa', 'recursos_disponiveis']
    date_hierarchy = 'criado_em'
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('empresa').annotate(
            candidaturas_count=Count('candidaturas')
        )

    def candidaturas_count(self, obj):
        count = getattr(obj, 'candidaturas_count', 0)
        if count > 0:
            url = reverse('admin:job_vacancies_candidatura_changelist') + f'?vaga__id__exact={obj.pk}'
            return format_html('<a href="{}" class="text-primary font-bold">{}</a>', url, count)
        return '0'
    candidaturas_count.short_description = 'Candidaturas'

    def empresa_link(self, obj):
        url = reverse('admin:account_user_change', args=[obj.empresa.pk])
        return format_html('<a href="{}">{}</a>', url, obj.empresa)
    empresa_link.short_description = 'Empresa'

    def status_badge(self, obj):
        colors = {
            'rascunho': 'badge-ghost',
            'aguardando_aprovacao': 'badge-warning',
            'aprovada': 'badge-success',
            'rejeitada': 'badge-error',
            'aberta': 'badge-info',
            'pausada': 'badge-secondary',
            'finalizada': 'badge-ghost',
        }
        color = colors.get(obj.status, 'badge-ghost')
        return format_html('<span class="badge {}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'


@admin.register(AvaliacaoVagaMedica)
class AvaliacaoVagaMedicaAdmin(admin.ModelAdmin):
    list_display = ['vaga_link', 'medico_link', 'status_badge', 'deficiencias_list', 'avaliado_em']
    list_filter = ['status', 'avaliado_em', 'medico']
    search_fields = ['vaga__titulo', 'medico__nome_completo']
    autocomplete_fields = ['vaga', 'medico']
    readonly_fields = ['avaliado_em']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vaga__empresa', 'medico').prefetch_related('deficiencias_elegiveis')

    def vaga_link(self, obj):
        url = reverse('admin:job_vacancies_vaga_change', args=[obj.vaga.pk])
        return format_html('<a href="{}">{}</a>', url, obj.vaga.titulo[:50])
    vaga_link.short_description = 'Vaga'

    def medico_link(self, obj):
        if obj.medico:
            url = reverse('admin:account_user_change', args=[obj.medico.pk])
            return format_html('<a href="{}">Dr(a). {}</a>', url, obj.medico.nome_completo)
        return "Não atribuído"
    medico_link.short_description = 'Médico'

    def deficiencias_list(self, obj):
        defs = obj.deficiencias_elegiveis.all()[:3]
        if not defs:
            return "Nenhuma"
        html = " • ".join([f'<span class="badge badge-sm badge-outline">{d.nome}</span>' for d in defs])
        if obj.deficiencias_elegiveis.count() > 3:
            html += f" +{obj.deficiencias_elegiveis.count() - 3}"
        return format_html(html)
    deficiencias_list.short_description = 'Deficiências Elegíveis'

    def status_badge(self, obj):
        colors = {
            'pendente': 'badge-warning',
            'aprovada': 'badge-success',
            'rejeitada': 'badge-error',
            'ajustes_necessarios': 'badge-secondary',
        }
        return format_html('<span class="badge {}">{}</span>', colors.get(obj.status, 'badge-ghost'), obj.get_status_display())
    status_badge.short_description = 'Status'


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ['pcd_link', 'vaga_link', 'status_badge', 'criado_em', 'avaliacao_empresa_stars']
    list_filter = ['status', 'vaga__empresa', 'criado_em']
    search_fields = ['pcd__nome_completo', 'vaga__titulo']
    autocomplete_fields = ['pcd', 'vaga']
    readonly_fields = ['criado_em', 'atualizado_em']

    def pcd_link(self, obj):
        url = reverse('admin:account_user_change', args=[obj.pcd.pk])
        return format_html('<a href="{}">{}</a>', url, obj.pcd)
    pcd_link.short_description = 'Candidato PCD'

    def vaga_link(self, obj):
        url = reverse('admin:job_vacancies_vaga_change', args=[obj.vaga.pk])
        return format_html('<a href="{}">{}</a>', url, obj.vaga.titulo[:40])
    vaga_link.short_description = 'Vaga'

    def avaliacao_empresa_stars(self, obj):
        if obj.avaliacao_empresa:
            return '★' * obj.avaliacao_empresa + '☆' * (5 - obj.avaliacao_empresa)
        return "—"
    avaliacao_empresa_stars.short_description = 'Nota Empresa'

    def status_badge(self, obj):
        colors = {
            'pendente': 'badge-warning',
            'aprovado': 'badge-success',
            'reprovado': 'badge-error',
            'entrevista_agendada': 'badge-info',
        }
        return format_html('<span class="badge {}">{}</span>', colors.get(obj.status, 'badge-ghost'), obj.get_status_display())
    status_badge.short_description = 'Status'


admin.site.register(Conversa)
admin.site.register(Mensagem)