from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from questions_answers.models import BaseModel


class User(BaseModel, AbstractUser):
    def get_absolute_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username
