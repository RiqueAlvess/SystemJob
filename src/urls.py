from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),

    path('account/forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='account/forgot_password.html',
        email_template_name='account/password_reset_email.html',
        subject_template_name='account/password_reset_subject.txt',
        success_url='/account/forgot-password/done/'
    ), name='forgot_password'),

    path('account/forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='account/forgot_password_done.html'
    ), name='forgot_password_done'),

    path('account/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html',
        success_url='/account/reset/done/'
    ), name='password_reset_confirm'),

    path('account/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html'
    ), name='password_reset_complete'),
]