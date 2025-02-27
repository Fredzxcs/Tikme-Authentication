from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import views
from django.shortcuts import render, get_object_or_404

from authentication.views.views_job_titles import validate_token
from ..emails import *
from ..models import *
from ..serializers import *
import jwt, datetime, logging
from django.utils.timezone import now
from django.core.cache import cache
from django.contrib.auth.hashers import check_password

logger = logging.getLogger(__name__)

# ✅ Landing Page View
class LandingPageView(views.APIView):
    """ Renders the landing page """
    def get(self, request):
        return render(request, 'admin_login.html')

# ✅ Login View with Security Features (No reCAPTCHA)
class LoginView(views.APIView):
    """ Handles user login with brute force protection and security questions """
    def get(self, request):
        return render(request, 'admin_login.html')

    def post(self, request):
        user_number = request.data.get('user_number')
        password = request.data.get('password')
        security_answers = request.data.get('security_answers', [])

        if not user_number or not password:
            raise AuthenticationFailed("❌ User number and password are required!")

        user = User.objects.filter(user_number=user_number).first()

        # ✅ User does not exist
        if not user:
            raise AuthenticationFailed("❌ Invalid credentials!")

        # ✅ Cache key for failed attempts tracking
        attempts_key = f"login_attempts_{user.id}"
        attempts = cache.get(attempts_key, 0)

        # ✅ Check if permanently locked
        if user.status.status_name == "Permanently Locked":
            raise AuthenticationFailed("🔒 Your account is permanently locked. Contact support.")

        # ✅ Handle Temporary Lock
        locked_until = cache.get(f"locked_until_{user.id}")
        if user.status.status_name == "Temporarily Locked":
            if locked_until and now() < locked_until:
                time_remaining = (locked_until - now()).seconds // 60
                raise AuthenticationFailed(f"⏳ Your account is temporarily locked. Try again in {time_remaining} minutes.")
            else:
                # ✅ Auto-unlock if time expired
                user.status = Status.objects.get_or_create(status_name="Active")[0]
                cache.delete(f"locked_until_{user.id}")
                user.failed_attempts = 0
                user.save()

        # ✅ Require security questions after 6 failed attempts
        if attempts >= 6:
            if not security_answers or len(security_answers) != 3:
                raise AuthenticationFailed("🔐 Answer security questions to proceed.")

            if not self.validate_security_answers(user, security_answers):
                logger.warning(f"🔐 Security answers mismatch for user: {user.email}")
                cache.set(attempts_key, attempts + 1, timeout=900)
                raise AuthenticationFailed("🔐 Security answers do not match.")

        # ✅ Authenticate user
        if not check_password(password, user.password):
            cache.set(attempts_key, attempts + 1, timeout=900)

            # 🔒 Temporary Lock (3 failed attempts)
            if attempts + 1 == 3:
                lock_duration = datetime.timedelta(minutes=15)
                cache.set(f"locked_until_{user.id}", now() + lock_duration, timeout=900)
                user.status = Status.objects.get_or_create(status_name="Temporarily Locked")[0]
                user.save()
                send_temp_locked_email(user)
                logger.warning(f"🚨 User {user.email} temporarily locked due to failed attempts.")
                raise AuthenticationFailed("🔒 Too many failed attempts. Your account is temporarily locked for 15 minutes.")

            # 🚨 Permanent Lock (9 failed attempts)
            if attempts + 1 >= 9:
                user.status = Status.objects.get_or_create(status_name="Permanently Locked")[0]
                user.save()
                send_permanent_locked_email(user)
                logger.critical(f"🚨 User {user.email} permanently locked due to excessive failed attempts.")
                raise AuthenticationFailed("🔒 Your account has been permanently locked. Contact support.")

            raise AuthenticationFailed("❌ Invalid credentials!")

        # ✅ Reset failed attempts on successful login
        cache.set(attempts_key, 0, timeout=900)
        user.failed_attempts = 0
        user.save()

        # ✅ Generate JWT Token
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        # ✅ Determine redirection URL
        redirection_url = self.get_redirection_url(user, token)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token, 'redirect_to': redirection_url}
        return response

    # ✅ Security Answers Validation
    def validate_security_answers(self, user, submitted_answers):
        """ Compares submitted security answers with stored answers """
        stored_answers = SecurityAnswer.objects.filter(user=user).values_list("question_id", "answer")

        # ✅ Convert to dictionary for easy lookup
        stored_dict = {str(qid): answer.lower() for qid, answer in stored_answers}

        for item in submitted_answers:
            question_id = str(item.get("question_id"))
            answer = item.get("answer", "").strip().lower()

            if question_id not in stored_dict or stored_dict[question_id] != answer:
                return False  # ❌ Mismatch found
        return True  # ✅ All answers match

    # ✅ Redirection Logic
    def get_redirection_url(self, user, token):
        """ Determines the correct redirection URL based on user role """
        if user.is_superuser:
            return "/manage-users/"
        elif user.role and user.role.role_name == "System Admin":
            return "/manage-users/"
        elif user.module and user.module.module_name == "Reservation":
            return f"{settings.RESERVATION_URL}?token={token}"
        elif user.module and user.module.module_name == "Logistic":
            return f"{settings.LOGISTIC_URL}?token={token}"
        elif user.module and user.module.module_name == "Finance":
            return f"{settings.FINANCE_URL}?token={token}"
        return "/unauthorized_access/"

# ✅ Unlock User View (Super Admin / System Admin Only)
class UnlockUserView(views.APIView):
    """ Handles unlocking users (removes temporary or permanent locks) """
    def post(self, request, pk):
        payload = validate_token(request)
        current_user = get_object_or_404(User, id=payload["id"])

        if current_user.role.role_name not in ["Super Admin", "System Admin"]:
            raise AuthenticationFailed("❌ You do not have permission to unlock users.")

        user = get_object_or_404(User, pk=pk)
        user.status = Status.objects.get_or_create(status_name="Active")[0]
        cache.delete(f"locked_until_{user.id}")
        user.failed_attempts = 0
        user.save()

        logger.info(f"✅ User {user.email} was unlocked by {current_user.email}.")
        return Response({"message": "✅ User unlocked successfully."}, status=200)

# ✅ Logout View
class LogoutView(views.APIView):
    """ Handles user logout by deleting JWT token """
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'success'}
        return render(request, "admin_login.html")

# ✅ Unauthorized Access View
class UnauthorizedAccessView(views.APIView):
    """ Renders the unauthorized access page """
    def get(self, request):
        return render(request, 'unauthorized_access.html')

class NotificationView(views.APIView):

    def get(self, request):
        # Get notifications related to the logged-in user
        user = request.user  
        notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
        
        # Render the notifications in the template
        return render(request, 'super_admin_sidebar.html', {'notifications': notifications})

