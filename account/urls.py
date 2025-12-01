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

    path("forgot-password/", views.PasswordResetView.request_view, name="forgot_password"),
    path("reset/<uidb64>/<token>/", views.PasswordResetView.confirm_view, name="password_reset_confirm"),
    path("reset/done/", views.PasswordResetView.complete_view, name="password_reset_complete"),
    path("forgot-password/sent/", views.PasswordResetView.sent_view, name="password_reset_sent"),
]