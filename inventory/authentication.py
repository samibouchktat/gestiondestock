from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

class EmailOrSecondaryEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) |
                Q(username__iexact=username) |
                Q(secondary_email__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
