from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from pyppi.util import get_anonymous_user, AnonUser


class AnonymousBackend(ModelBackend):
    """
    Authenticates against django.contrib.auth.models.User.
    """
    supports_inactive_user = True

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            if username and username.lower() == 'anonymous':
                return get_anonymous_user()
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            if user_id == settings.ANONYMOUS_USER_ID:
                return AnonUser.objects.get(pk=settings.ANONYMOUS_USER_ID)
        except User.DoesNotExist:
            return None

