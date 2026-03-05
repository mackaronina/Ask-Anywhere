from django.contrib.auth.models import AbstractUser

from questions_answers.models import BaseModel


class User(BaseModel, AbstractUser):
    def __str__(self):
        return self.username
