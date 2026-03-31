from django.urls import path
from django.contrib.auth.views import (
    LoginView, 
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    # Маршрути для скидання пароля
    path('reset-password/', 
         PasswordResetView.as_view(template_name='registration/password_reset_form.html', 
                                   email_template_name='registration/password_reset_email.html',
                                   success_url='/users/reset-password/done/'), 
         name='password_reset'),
    
    path('reset-password/done/', 
         PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    
    path('reset-password/confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',
                                          success_url='/users/reset-password/complete/'), 
         name='password_reset_confirm'),
    
    path('reset-password/complete/', 
         PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]