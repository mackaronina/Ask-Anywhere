import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Question(BaseModel):
    title = models.CharField(max_length=128)
    text = models.CharField(max_length=4096)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='questions', null=True,
                             default=None)

    def get_rating(self):
        return self.votes.filter(is_positive=True).count() - self.votes.filter(is_positive=False).count()

    def get_answers_count(self):
        return self.answers.count()

    def has_solution(self):
        return self.answers.filter(is_solution=True).exists()

    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'pk': self.pk})

    def get_vote(self, user):
        if not user.is_authenticated:
            return None
        return self.votes.filter(user=user).first()

    def __str__(self):
        return f'"{self.title}" by {self.user}'


class Answer(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=4096)
    is_solution = models.BooleanField(default=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='answers', null=True,
                             default=None)

    def get_rating(self):
        return self.votes.filter(is_positive=True).count() - self.votes.filter(is_positive=False).count()

    def get_absolute_url(self):
        return f'{self.question.get_absolute_url()}?answer_id={self.pk}'

    def get_vote(self, user):
        if not user.is_authenticated:
            return None
        return self.votes.filter(user=user).first()

    def __str__(self):
        return f'"{self.text[:128]}" by {self.user}'


class VoteQuestion(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    is_positive = models.BooleanField(default=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='questions_votes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'user'], name='unique_vote_question')
        ]

    @property
    def is_negative(self):
        return not self.is_positive

    def __str__(self):
        return f'Positive vote by {self.user}' if self.is_positive else f'Negative vote by {self.user}'

    def get_absolute_url(self):
        return self.question.get_absolute_url()


class VoteAnswer(BaseModel):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    is_positive = models.BooleanField(default=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='answers_votes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['answer', 'user'], name='unique_vote_answer')
        ]

    @property
    def is_negative(self):
        return not self.is_positive

    def __str__(self):
        return f'Positive vote by {self.user}' if self.is_positive else f'Negative vote by {self.user}'

    def get_absolute_url(self):
        return self.answer.get_absolute_url()
