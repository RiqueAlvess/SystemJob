# job_vacancies/urls.py
from django.urls import path
from . import views

app_name = "job_vacancies"

urlpatterns = [
    path("minhas-vagas/", views.MinhasVagasListView.as_view(), name="minhas_vagas"),
    path("vaga/nova/", views.VagaCreateView.as_view(), name="vaga_create"),
    path("vaga/<int:pk>/", views.VagaDetailView.as_view(), name="vaga_detail"),
    path("vaga/<int:pk>/editar/", views.VagaUpdateView.as_view(), name="vaga_edit"),
    path("vaga/<int:pk>/submeter/", views.VagaSubmeterAprovacaoView.as_view(), name="vaga_submeter"),
    path("vaga/<int:pk>/publicar/", views.VagaPublicarView.as_view(), name="vaga_publicar"),
    path("vaga/<int:pk>/pausar/", views.VagaPausarView.as_view(), name="vaga_pausar"),
    path("vaga/<int:pk>/finalizar/", views.VagaFinalizarView.as_view(), name="vaga_finalizar"),

    #Remover
    path("feed/", views.FeedVagasPCDView.as_view(), name="feed_pcd"),
    path("candidatar/<int:vaga_id>/", views.CandidatarView.as_view(), name="candidatar"),
]