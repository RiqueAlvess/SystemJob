from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.utils import timezone
from account.models import User, CategoriaDeficiencia


class RecursoAcessibilidade(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    icone = models.CharField(max_length=50, blank=True) 
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Recurso de Acessibilidade"
        verbose_name_plural = "Recursos de Acessibilidade"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Vaga(models.Model):
    TIPO_CHOICES = [
        ('emprego', 'Emprego'),
        ('capacitacao', 'Capacitação'),
    ]

    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('aguardando_aprovacao', 'Aguardando Aprovação Médica'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('aberta', 'Aberta'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
    ]

    empresa = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='vagas', limit_choices_to={'tipo': 'empresa'}
    )
    titulo = models.CharField("Título da Vaga", max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='emprego')
    modalidade = models.CharField(max_length=20, choices=[('presencial', 'Presencial'), ('remoto', 'Remoto'), ('hibrido', 'Híbrido')])
    localizacao = models.CharField(max_length=255, blank=True)
    salario_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salario_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mostrar_salario = models.BooleanField(default=False)
    recursos_disponiveis = models.ManyToManyField(RecursoAcessibilidade, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='rascunho', db_index=True)
    visualizacoes = models.PositiveIntegerField(default=0, editable=False)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    publicado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Vaga"
        verbose_name_plural = "Vagas"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['empresa', 'status']),
            GinIndex(fields=['titulo', 'descricao']),  # para busca full-text futura
        ]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.titulo} - {self.empresa}"

    def pode_ser_editada(self):
        return self.status in ['rascunho', 'rejeitada', 'pausada']

    def pode_ser_submetida(self):
        return self.status == 'rascunho'

    def publicar(self):
        if self.status == 'aprovada':
            self.status = 'aberta'
            self.publicado_em = timezone.now()
            self.save(update_fields=['status', 'publicado_em'])


class AvaliacaoVagaMedica(models.Model):
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='avaliacoes_medicas')
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='avaliacoes_feitas')
    deficiencias_elegiveis = models.ManyToManyField(CategoriaDeficiencia, blank=True)
    status = models.CharField(max_length=30, choices=[
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('ajustes_necessarios', 'Ajustes Necessários'),
    ], default='pendente')
    observacoes = models.TextField(blank=True)
    ajustes_recomendados = models.TextField(blank=True)
    avaliado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Avaliação Médica da Vaga"
        ordering = ['-avaliado_em']

    def __str__(self):
        return f"Avaliação de {self.vaga} por {self.medico}"


class Candidatura(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('visualizado', 'Visualizado'),
        ('em_analise', 'Em Análise'),
        ('pre_selecionado', 'Pré-selecionado'),
        ('entrevista_agendada', 'Entrevista Agendada'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('desistente', 'Desistente'),
    ]

    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='candidaturas')
    pcd = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidaturas', limit_choices_to={'tipo': 'pcd'})
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pendente', db_index=True)
    mensagem_candidato = models.TextField(blank=True)
    avaliacao_empresa = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    observacoes_empresa = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vaga', 'pcd')
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['vaga', 'status']),
        ]

    def __str__(self):
        return f"{self.pcd} → {self.vaga.titulo}"


class Conversa(models.Model):
    candidatura = models.OneToOneField(Candidatura, on_delete=models.CASCADE, related_name='conversa')

    def mensagens_nao_lidas_empresa(self):
        return self.mensagens.filter(lida_por_empresa=False).count()

    def mensagens_nao_lidas_pcd(self):
        return self.mensagens.filter(lida_por_pcd=False).count()


class Mensagem(models.Model):
    REMETENTE_CHOICES = [
        ('empresa', 'Empresa'),
        ('pcd', 'PCD'),
    ]

    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    remetente_tipo = models.CharField(max_length=10, choices=REMETENTE_CHOICES)
    conteudo = models.TextField()
    anexo = models.FileField(upload_to='chat_anexos/%Y/%m/', null=True, blank=True)
    enviado_em = models.DateTimeField(auto_now_add=True)
    lida_por_empresa = models.BooleanField(default=False)
    lida_por_pcd = models.BooleanField(default=False)

    class Meta:
        ordering = ['enviado_em']