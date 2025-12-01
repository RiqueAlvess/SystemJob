from django.urls import path
from .views import (
    DashboardDoctorView,
    FilaAprovacaoView,
    AvaliarVagaView,
)

app_name = "doctor"

urlpatterns = [
    path("", DashboardDoctorView.as_view(), name="dashboard"),
    path("fila/", FilaAprovacaoView.as_view(), name="fila"),
    path("avaliar/<int:pk>/", AvaliarVagaView.as_view(), name="avaliar_vaga"),
]