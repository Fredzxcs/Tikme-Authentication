from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views.views_setup import (
    # Account Setup Views
    setup_account,
    setup_password,
    setup_security_questions,
)

from .views.views_system_admin import (
    # Additional Views
    system_admin_dashboard,
    add_employee,
    change_status,

    # Email Actions
    send_onboarding_email,
)

from .views.views_admin import (
    # Admin Actions
    admin_login,
    send_reset_password_email,

    # Password Management
    forgot_password,
    reset_password,
    tech_support,

    # Reactivation Views
    reactivate_account,

    # Email Notification Views
    send_account_locked_email,
    send_permanently_locked_email,
    
    # Authentication Views (if using custom JWT)
    jwt_authenticate,
    unauthorized_access,
    invalid_link,
)

urlpatterns = [
    # JWT Authentication URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Account Setup
    path('setup_account/<str:uidb64>/<str:token>/', setup_account, name='setup_account'),
    path('setup_password/<str:uidb64>/<str:token>/', setup_password, name='setup_password'),
    path('setup_security_questions/', setup_security_questions, name='setup_security_questions'),

    # Admin Actions
    path('', admin_login, name='admin_login'),
    path('send_reset_password_email/', send_reset_password_email, name='send_reset_password_email'),

    # Password Management
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', reset_password, name='reset_password'),
    path('tech_support/', tech_support, name='tech_support'),

    # System Admin Views
    path('system_admin_dashboard/', system_admin_dashboard, name='system_admin_dashboard'),
    path('add_employee/', add_employee, name='add_employee'),
    path('change_status/<int:employee_id>/<str:status>/', change_status, name='change_status'),

    # Email Actions
    path('send_onboarding_email/', send_onboarding_email, name='send_onboarding_email'),

    # Reactivate Account
    path('reactivate_account/<uidb64>/<token>/', reactivate_account, name='reactivate_account'),

    # Locked Account Email Notifications
    path('send_account_locked_email/', send_account_locked_email, name='send_account_locked_email'),
    path('send_permanently_locked_email/', send_permanently_locked_email, name='send_permanently_locked_email'),

    # Custom JWT Authentication/Authorization (if necessary)
    path('jwt_authenticate/', jwt_authenticate, name='jwt_authenticate'),
    path('unauthorized_access/', unauthorized_access, name='unauthorized_access'),
    path('invalid_link/', invalid_link, name='invalid_link'),
]
