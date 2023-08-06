from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (1, 5):
    # Django 1.5+ compatibility
    from django.contrib.auth import get_user_model
    User = get_user_model()

else:
    from django.contrib.auth.models import User
