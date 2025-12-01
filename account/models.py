from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        ext = 'webp'
    year = timezone.now().strftime('%Y')
    month = timezone.now().strftime('%m')
    timestamp = int(timezone.now().timestamp() * 1000000)
    return f"avatars/{year}/{month}/{instance.user.pk}_{timestamp}.{ext}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('E-mail', unique=True)
    nome_completo = models.CharField('Nome completo', max_length=255)

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro/Prefiro não dizer')
    ]
    sexo = models.CharField('Sexo', max_length=1, choices=SEXO_CHOICES, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)

    avatar_id = models.PositiveBigIntegerField(
        null=True, blank=True, editable=False, db_index=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usuarios_criados', editable=False
    )
    modificado_em = models.DateTimeField(auto_now=True)
    modificado_por = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usuarios_modificados', editable=False
    )
    ultima_sessao = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome_completo']
    objects = UserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome_completo.strip() or self.email or f"Usuário {self.pk}"

    def save(self, *args, **kwargs):
        kwargs.pop('request', None)
        kwargs.pop('atualizar_sessao', False)
        super().save(*args, **kwargs)

    def get_foto_url(self):
        avatar = self.avatars.filter(is_atual=True).first()
        return avatar.imagem.url if avatar and avatar.imagem else '/static/img/avatar-default.png'

    @property
    def eh_pcd(self):
        return hasattr(self, 'perfil_pcd')

    @property
    def eh_medico(self):
        return hasattr(self, 'perfil_medico')
    
    @property
    def eh_empresa(self):
        return hasattr(self, 'perfil_empresa')
    
    @property
    def tipo(self):
        if self.is_superuser or self.is_staff:
            return 'admin'
        if self.eh_pcd:
            return 'pcd'
        if self.eh_empresa:
            return 'empresa'
        if self.eh_medico:
            return 'medico'
        return 'desconhecido'
    
    @property
    def primeiro_nome(self):
        return self.nome_completo.split()[0] if self.nome_completo else ""


class UserAvatar(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='avatars'
    )
    imagem = models.ImageField(
        upload_to=avatar_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='Imagem do Avatar',
        help_text='Formatos aceitos: JPG, PNG, WEBP.',
        max_length=500
    )
    is_atual = models.BooleanField(default=True, verbose_name='Avatar atual')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avatar de Usuário'
        verbose_name_plural = 'Avatares de Usuário'
        ordering = ['-criado_em']
        unique_together = ('user', 'is_atual')

    def __str__(self):
        return f"Avatar de {self.user}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if self.imagem:
            img = Image.open(self.imagem)
            
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            self.imagem = InMemoryUploadedFile(
                output, 'ImageField', 
                f"{self.imagem.name.split('.')[0]}.jpg",
                'image/jpeg', output.getbuffer().nbytes, None
            )

        super().save(*args, **kwargs)
        
        if is_new:
            UserAvatar.objects.filter(user=self.user).exclude(pk=self.pk).update(is_atual=False)
            self.user.avatar_id = self.pk
            self.user.save(update_fields=['avatar_id'])

    def delete(self, *args, **kwargs):
        storage, path = self.imagem.storage, self.imagem.path
        super().delete(*args, **kwargs)
        if storage.exists(path):
            storage.delete(path)


class PerfilPCD(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_pcd')
    cpf = models.CharField('CPF', max_length=14, unique=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    status_medico = models.CharField('Status Médico', max_length=20, default='pendente', choices=[
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado')
    ])
    percentual_perfil = models.DecimalField('Percentual de Perfil', max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Perfil PCD de {self.user}"


class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome


class PerfilMedico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_medico')
    crm = models.CharField('CRM', max_length=15, unique=True)
    uf_crm = models.CharField('UF do CRM', max_length=2)
    especialidades = models.ManyToManyField('Especialidade', blank=True)

    def __str__(self):
        return f"Dr(a). {self.user} - {self.crm}"


class PerfilEmpresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_empresa')
    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
    razao_social = models.CharField('Razão Social', max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True)
    telefone_principal = models.CharField(max_length=20)
    telefone_secundario = models.CharField(max_length=20, blank=True)
    site = models.URLField(blank=True)

    def __str__(self):
        return self.razao_social or self.nome_fantasia or f"Empresa {self.user}"


class CategoriaDeficiencia(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoria de Deficiência'
        verbose_name_plural = 'Categorias de Deficiência'

    def __str__(self):
        return self.nome