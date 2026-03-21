from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from AskAnywhere import settings


class UsersConfig(AppConfig):
    name = 'users'

    # Creating an account for the AI assistant
    def ready(self):
        if not settings.AI_HELPER_ENABLED:
            return
        user_model = get_user_model()
        user = user_model(username=settings.AI_HELPER_USERNAME, is_active=False)
        try:
            user.save()
        except IntegrityError:
            pass
