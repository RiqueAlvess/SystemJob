from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("register/", views.RegisterChoiceView.as_view(), name="register_choice"),
    path("register/pcd/", views.RegisterPCDView.as_view(), name="register_pcd"),
    path("register/company/", views.RegisterCompanyView.as_view(), name="register_company"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("panel/", views.PanelView.as_view(), name="panel"),
]