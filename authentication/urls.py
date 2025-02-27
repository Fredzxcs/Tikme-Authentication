from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    # Authentication and General Access
    path('', views_auth.LandingPageView.as_view(), name='landing_page'),
    path('admin_login/', views_auth.LoginView.as_view(), name='admin_login'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),

    # System Admin Dashboard
    path('tech_support/', views_emails.TechSupportView.as_view(), name='tech_support'),

    # Forgot Password
    path('forgot_password/', views_forgot_password.ForgotPasswordView.as_view(), name='forgot_password'),
    # Reset Password - Setup Questions
    path('forgot-setup-questions/<str:uidb64>/<str:token>/', views_forgot_password.ForgotSetupQuestionsView.as_view(), name='forgot_setup_questions'),
    # Reset Password - Setup Password
    path('reset-password/<str:uidb64>/<str:token>/change-password/', views_forgot_password.ForgotSetupPasswordView.as_view(), name='forgot_setup_password'),
    
    path('validate-password/', views_forgot_password.validate_password, name='validate_password'),

    path('send-email/<int:user_id>/onboarding/', views_emails.SendOnboardingEmailView.as_view(), name='send_onboarding_email'),
    path('send-email/<int:user_id>/locked/', views_emails.SendLockedEmailView.as_view(), name='send_locked_email'),
    path('send-email/<int:user_id>/reactivation/', views_emails.SendReactivationEmailView.as_view(), name='send_reactivation_email'),

    path('setup-account/<str:uidb64>/<str:token>/', views_setup_account.SetupAccountView.as_view(), name='setup_account'),
    path('setup-password/<str:uidb64>/<str:token>/', views_setup_account.SetupPasswordView.as_view(), name='setup_password'),
    path('refresh-token/', views_setup_account.RefreshTokenView.as_view(), name='refresh_token'),

    path('manage-users/', views_manage_users.ManageUsersView.as_view(), name='manage-users'),
    path('add-user/', views_manage_users.AddUserView.as_view(), name='add_user'),
    path('manage-users/<int:pk>/edit/', views_manage_users.EditUserView.as_view(), name='edit_user'),
    path('manage-users/<int:pk>/delete/', views_manage_users.DeleteUserView.as_view(), name='delete_user'),
    path('email-actions/<int:pk>/', views_manage_users.EmailActionsView.as_view(), name='email-actions'),
    path('status-actions/<int:pk>/', views_manage_users.StatusActionsView.as_view(), name='status-actions'),
    path("verify-email/<str:token>/", views_manage_users.VerifyEmailView.as_view(), name="verify-email"),
    
    path('job-titles/', views_job_titles.JobTitleListCreateView.as_view(), name='job-titles'),
    path('job-titles/<int:pk>/', views_job_titles.JobTitleDetailView.as_view(), name='job-titles-detail'),

    path('modules/', views_modules.ModuleListCreateView.as_view(), name='modules'),
    path('modules/<int:pk>/', views_modules.ModuleDetailView.as_view(), name='modules-detail'),
    
    # Super Admin-Specific Actions
    path('permissions/', views_permissions.PermissionListCreateView.as_view(), name='permissions'),
    path('permissions/<int:pk>/', views_permissions.PermissionDetailView.as_view(), name='permissions-detail'),
    path('job-titles/<int:job_title_id>/assign-permission/', views_permissions.AssignPermissionToJobTitleView.as_view(), name='assign-permission'),
    path('job-titles-with-permissions/', views_permissions.JobTitleWithPermissionsView.as_view(), name='job-titles-with-permissions'),
    path('api/job-titles/<int:job_title_id>/permissions/', views_permissions.JobTitlePermissionsView.as_view(), name='job-title-permissions'),
    path('job-titles/<int:job_title_id>/remove-permission/<int:permission_id>/', views_permissions.RemovePermissionFromJobTitleView.as_view(), name='remove-permission'),
    path('job-titles/<int:job_title_id>/remove-all-permissions/', views_permissions.RemoveAllPermissionsFromJobTitleView.as_view(), name='remove-all-permissions'),
    path('roles/', views_roles.RoleListCreateView.as_view(), name='roles'),
    path('roles/<int:pk>/', views_roles.RoleDetailView.as_view(), name='roles-detail'),

    path('unauthorized_access/', views_auth.UnauthorizedAccessView.as_view(), name='unauthorized_access'),
    path('notifications/', views_auth.NotificationView.as_view(), name='notifications'),

    # ✅ Profile URLs
    path('profile/', views_profile.ProfileView.as_view(), name='profile'),
    path('profile/<str:user_identifier>/', views_profile.ProfileDetailView.as_view(), name='profile-detail'),  # Fetch specific user profile

    # ✅ Account Settings URLs
    path('account_settings/', views_profile.AccountSettingsView.as_view(), name='account_settings'),
    path('account-settings/<str:user_identifier>/', views_profile.AccountSettingsDetailView.as_view(), name='account-settings-detail'),  # Fetch specific user settings
]

# Serve media files in development (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
