from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static
from django.urls import reverse

from questions_answers.models import BaseModel


class User(BaseModel, AbstractUser):
    photo_url = models.URLField(max_length=200, default=static('users/images/default.png'))

    def get_absolute_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.username
