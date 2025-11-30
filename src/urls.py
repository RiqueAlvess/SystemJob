from django.contrib import admin
from django.urls import path, include
from account.views import CustomPasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),

    path('account/forgot-password/', CustomPasswordResetView.as_view(), name='forgot_password'),
    path('account/forgot-password/done/', CustomPasswordResetView.done_view, name='forgot_password_done'),
    path('account/reset/<uidb64>/<token>/', CustomPasswordResetView.confirm_view, name='password_reset_confirm'),
    path('account/reset/done/', CustomPasswordResetView.complete_view, name='password_reset_complete'),
]