import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

# Configure logger for authentication utilities
logger = logging.getLogger('authentication')

def jwt_authenticate(request):
    """
    Extracts and validates the JWT token from the Authorization header of the request.
    Returns the authenticated user or None if authentication fails.
    """
    # Get the Authorization header from the request
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        # Extract the token after "Bearer "
        token = auth_header.split(' ')[1]
        try:
            # Validate the token using DRF's SimpleJWT
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            logger.info(f"User {user.username} authenticated successfully.")
            return user
        except AuthenticationFailed as e:
            # Log authentication failure
            logger.warning(f"JWT Authentication failed: {e}")
            return None
    else:
        # Log missing or invalid Authorization header
        logger.warning("No valid Authorization header found in request.")
        return None
