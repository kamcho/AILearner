from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView, MyProfile, Home

urlpatterns = [

    path('register/',RegisterView.as_view(),name='register'),
    path('<int:pk>/info/',MyProfile.as_view(),name='profile'),
    path('',Home.as_view(),name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='Users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='Users/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='Users/password_reset.html'), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='Users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='Users/password_reset_complete.html'),name='password_reset_complete'),

]