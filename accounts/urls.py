# accounts/urls.py

from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('buscar-lojas/', get_lojas_by_username, name='buscar_lojas'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('profile/', MyProfileView.as_view(), name='profile'),
    
    path('gropos/', GroupListView.as_view(), name='group_list'),
    path('gropos/novo/', GroupCreateView.as_view(), name='group_create'),
    path('gropos/editar/<int:pk>/', GroupUpdateView.as_view(), name='group_update'),
    
    path('permissions/', PermissionsListView.as_view(), name='permissions_list'),
    # path('gropos/deletar/<int:pk>/', GroupDeleteView.as_view(), name='group_delete'),
    
    path('users/', UserListView.as_view(), name='user_list'),

    path('autorizacao/', get_autorizacao_user, name='autorizacao_user'),
]
