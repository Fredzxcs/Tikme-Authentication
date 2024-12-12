from django.urls import path
from .views import *


urlpatterns = [

    # Admin Actions
    path('', views_static.landing_page, name='admin_login'),

    # JWT Authentication URLs
    path('register/', views_auth.RegisterView.as_view(), name='register'),
    path('login/', views_auth.LoginView.as_view(), name='login'),
    path('user/', views_auth.UserView.as_view(), name='user'),
    path('logout/', views_auth.LogoutView.as_view(), name='logout'),

    # Password Management
    path('forgot_password/', views_static.forgot_pass, name='forgot_password'),
    # path('reset_password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('tech_support/', views_static.tech_support, name='tech_support'),

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Account Setup
    # path('setup_account/<str:uidb64>/<str:token>/', setup_account, name='setup_account'),
    # path('setup_password/<str:uidb64>/<str:token>/', setup_password, name='setup_password'),
    # path('setup_security_questions/', setup_security_questions, name='setup_security_questions'),

    # path('send_reset_password_email/', send_reset_password_email, name='send_reset_password_email'),

    # # System Admin Views
    # path('system_admin_dashboard/', system_admin_dashboard, name='system_admin_dashboard'),
    # path('add_employee/', add_employee, name='add_employee'),
    # path('change_status/<int:employee_id>/<str:status>/', change_status, name='change_status'),

    # # Email Actions
    # path('send_onboarding_email/', send_onboarding_email, name='send_onboarding_email'),

    # # Reactivate Account
    # path('reactivate_account/<uidb64>/<token>/', reactivate_account, name='reactivate_account'),

    # # Locked Account Email Notifications
    # path('send_account_locked_email/', send_account_locked_email, name='send_account_locked_email'),
    # path('send_permanently_locked_email/', send_permanently_locked_email, name='send_permanently_locked_email'),

    # # Custom JWT Authentication/Authorization (if necessary)
    # path('jwt_authenticate/', jwt_authenticate, name='jwt_authenticate'),
    # path('unauthorized_access/', unauthorized_access, name='unauthorized_access'),
    # path('invalid_link/', invalid_link, name='invalid_link'),
]
