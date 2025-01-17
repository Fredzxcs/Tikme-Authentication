from django.urls import path
from .views import *

urlpatterns = [
    # Authentication and General Access
    path('', views_auth.LandingPageView.as_view(), name='landing_page'),
    path('admin_login/', views_auth.LoginView.as_view(), name='admin_login'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),

    # path('job-titles/', views_manage_users.JobTitleListCreateView.as_view(), name='job-title-list-create'),
    # path('status/', views_manage_users.StatusListCreateView.as_view(), name='status-create'),
    # path('status/<int:pk>/', views_manage_users.StatusDetailView.as_view(), name='status-detail'),
    # path('questions/', views_manage_users.QuestionsListCreateView.as_view(), name='questions-create'),
    # path('questions/<int:pk>/', views_manage_users.QuestionsDetailView.as_view(), name='questions-detail'),

    # System Admin Dashboard
    path('system_admin_dashboard/', views_dashboard.SystemAdminDashboardView.as_view(), name='system_admin_dashboard'),
    
    path('tech_support/', views_emails.TechSupportView.as_view(), name='tech_support'),
    path("forgot_password/", views_emails.ForgotPasswordView.as_view(), name="forgot_password"),
    path('send-email/<int:employee_id>/onboarding/', views_emails.SendOnboardingEmailView.as_view(), name='send_onboarding_email'),
    path('send-email/<int:employee_id>/locked/', views_emails.SendLockedEmailView.as_view(), name='send_locked_email'),
    path('send-email/<int:employee_id>/reactivation/', views_emails.SendReactivationEmailView.as_view(), name='send_reactivation_email'),

    path('manage-users/', views_manage_users.ManageUsersView.as_view(), name='manage_users'),
     path('add-employee/', views_manage_users.AddUserView.as_view(), name='add_employee'),
    path('manage-users/<int:pk>/edit/', views_manage_users.EditUserView.as_view(), name='edit_user'),
    path('manage-users/<int:pk>/delete/', views_manage_users.DeleteUserView.as_view(), name='delete_user'),
    path('email-actions/<int:pk>/', views_manage_users.EmailActionsView.as_view(), name='email-actions'),
    path('status-actions/<int:pk>/', views_manage_users.StatusActionsView.as_view(), name='status-actions'),
    
    # path('status/', views_manage_users.StatusListCreateView.as_view(), name='status-create'),
    # path('status/<int:pk>/', views_manage_users.StatusDetailView.as_view(), name='status-detail'),

    path('job-titles/', views_job_titles.JobTitleListCreateView.as_view(), name='job_titles'),
    path('job-titles/<int:pk>/', views_job_titles.JobTitleDetailView.as_view(), name='job_titles_detail'),

    path('modules/', views_modules.ModuleListCreateView.as_view(), name='modules'),
    path('modules/<int:pk>/', views_modules.ModuleDetailView.as_view(), name='modules-detail'),
    
    # Super Admin-Specific Actions
    path('permissions/', views_permissions.PermissionListCreateView.as_view(), name='permissions'),
    path('permissions/<int:pk>/', views_permissions.PermissionDetailView.as_view(), name='permissions-detail'),

    path('roles/', views_roles.RoleListCreateView.as_view(), name='roles'),
    path('roles/<int:pk>/', views_roles.RoleDetailView.as_view(), name='roles-detail'),
    path('roles/<int:role_id>/assign-permission/', views_permissions.AssignPermissionToRoleView.as_view(), name='assign-permission'),
    path('roles-with-permissions/', views_permissions.RoleWithPermissionsView.as_view(), name='roles-with-permissions'),

    path('unauthorized_access/', views_auth.UnauthorizedAccessView.as_view(), name='unauthorized_access'),
    # Utility and Static Pages
]

