from django.urls import path
from .views import *

urlpatterns = [

    # Admin Actions and Authentication
    path('', views_auth.LandingPageView.as_view(), name='landing_page'),
    path('admin_login/', views_auth.LoginView.as_view(), name='admin_login'),
    path('success/', views_static.success_page, name='admin_login'),
    path('system_admin_dashboard/', views_auth.SystemAdminDashboardView.as_view(), name='system_admin_dashboard'),
    path('register/', views_auth.RegisterView.as_view(), name='register'),
    path('register-util/<int:pk>/', views_auth.RegisterViewRUD.as_view(), name='register-util'),
    path('users/', views_auth.UserView.as_view(), name='users'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),

    # Entity Management: Groups, Employees, Roles, Modules, Job Titles, Statuses, Questions
    path('groups/', views_super_admin.GroupListView.as_view(), name='groups'),
    path('groups/<int:pk>/', views_super_admin.GroupDetailView.as_view(), name='groups-detail'),
    path('employees/', views_create.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', views_create.EmployeeDetailView.as_view(), name='employee-detail'),
    path('job-titles/', views_create.JobTitleListCreateView.as_view(), name='job-title-list-create'),
    path('roles/', views_create.RoleListCreateView.as_view(), name='role-list-create'),
    path('modules/', views_create.ModuleListCreateView.as_view(), name='module-list-create'),
    path('job-titles/', views_create.JobTitleListCreateView.as_view(), name='job-title-list-create'),
    path('status/', views_create.StatusListCreateView.as_view(), name='status-create'),
    path('status/<int:pk>/', views_create.StatusDetailView.as_view(), name='status-detail'),
    path('questions/', views_create.QuestionsListCreateView.as_view(), name='questions-create'),
    path('questions/<int:pk>/', views_create.QuestionsDetailView.as_view(), name='questions-detail'),
   
    path('manage-users/', views_create.ManageUsersView.as_view(), name='manage_users'),
    path('manage-users/add/', views_create.AddUserView.as_view(), name='add_user'),
    path('manage-users/<int:pk>/edit/', views_create.EditUserView.as_view(), name='edit_user'),
    path('manage-users/<int:pk>/delete/', views_create.DeleteUserView.as_view(), name='delete_user'),

    # Email and Password Management
    path('forgot_password/', views_static.forgot_pass, name='forgot_password'),
    path('tech_support/', views_emails.TechSupportView.as_view(), name='tech_support'),
    path('send-onboarding-email/<int:pk>/', views_emails.OnboardingEmailView.as_view(), name='send-onboarding-email'),

    # Utility and Static Pages
    path('unauthorized_access/', views_static.unauthorized_access, name='unauthorized_access'),
]
