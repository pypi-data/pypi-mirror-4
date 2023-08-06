# -*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailAuthBackend(ModelBackend):
    """
    Email based authentication backend.
    
    Install with:
    AUTHENTICATION_BACKENDS = (
        'inoa.backends.email_auth.backend.EmailAuthBackend',
        'django.contrib.auth.backends.ModelBackend',
    )
    """
    def authenticate(self, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
