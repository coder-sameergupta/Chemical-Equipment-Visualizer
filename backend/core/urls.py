from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    FileUploadView, SummaryView, HistoryView, EquipmentListView, PDFReportView,
    UserListView, ProfileView, RegisterView, PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('summary/<int:upload_id>/', SummaryView.as_view(), name='summary'),
    path('history/', HistoryView.as_view(), name='history'),
    path('data/<int:upload_id>/', EquipmentListView.as_view(), name='equipment-list'),
    path('report/<int:upload_id>/', PDFReportView.as_view(), name='pdf-report'),
]
