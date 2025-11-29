from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserAvatar, PerfilPCD, PerfilMedico, PerfilEmpresa

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'nome_completo', 'tipo_usuario', 'is_staff', 'is_superuser', 'criado_em']
    list_filter = ['is_staff', 'is_superuser', 'criado_em']  # REMOVIDO 'tipo'
    search_fields = ['email', 'nome_completo']
    ordering = ['-criado_em']
    readonly_fields = ['criado_em', 'ultima_sessao', 'avatar_preview']

    fieldsets = (
        ('Informações Pessoais', {'fields': ('email', 'nome_completo', 'sexo', 'telefone')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Datas', {'fields': ('criado_em', 'ultima_sessao')}),
        ('Avatar', {'fields': ('avatar_preview',)}),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'nome_completo', 'password1', 'password2', 'is_staff', 'is_superuser')
        }),
    )

    def tipo_usuario(self, obj):
        tipo = obj.tipo
        cores = {
            'admin': 'badge badge-error',
            'pcd': 'badge badge-success',
            'empresa': 'badge badge-primary',
            'medico': 'badge badge-warning',
            'desconhecido': 'badge badge-ghost'
        }
        return format_html(f'<span class="{cores.get(tipo, "badge")}">{tipo.upper()}</span>')
    tipo_usuario.short_description = 'Tipo'

    def avatar_preview(self, obj):
        url = obj.get_foto_url()
        if url and 'default' not in url:
            return format_html('<img src="{}" style="width:80px; height:80px; object-fit:cover; border-radius:50%;">', url)
        return "Sem avatar"
    avatar_preview.short_description = 'Foto atual'

@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = ['user', 'criado_em', 'is_atual']
    list_filter = ['is_atual', 'criado_em']
    readonly_fields = ['user', 'imagem', 'criado_em']

@admin.register(PerfilPCD)
class PerfilPCDAdmin(admin.ModelAdmin):
    list_display = ['user', 'cpf', 'status_medico', 'percentual_perfil']
    search_fields = ['user__email', 'user__nome_completo', 'cpf']
    list_filter = ['status_medico']

@admin.register(PerfilMedico)
class PerfilMedicoAdmin(admin.ModelAdmin):
    list_display = ['user', 'crm', 'uf_crm']
    search_fields = ['user__email', 'crm']

@admin.register(PerfilEmpresa)
class PerfilEmpresaAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'cnpj', 'user']
    search_fields = ['razao_social', 'cnpj', 'user__email']