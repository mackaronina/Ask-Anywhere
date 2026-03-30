import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Q
from django.urls import reverse
from martor.models import MartorField
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def is_relation_loaded(self, field_name: str) -> bool:
        if hasattr(self, '_prefetched_objects_cache') and field_name in self._prefetched_objects_cache:
            return True
        if field_name in self._state.fields_cache:
            return True
        return False


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    pass


class Vote(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_positive = models.BooleanField(default=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='votes')

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['object_id', 'user'], name='unique_vote')
        ]

    @property
    def is_negative(self):
        return not self.is_positive

    def __str__(self):
        return f'Positive by {self.user}' if self.is_positive else f'Negative by {self.user}'

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()


class VotesModel(BaseModel):
    votes = GenericRelation(Vote)

    class Meta:
        abstract = True

    def get_vote(self, user):
        if not user.is_authenticated:
            return None
        if not self.is_relation_loaded('votes'):
            return self.votes.filter(user=user).first()
        votes = self.votes.all()
        for vote in votes:
            if vote.user_id == user.pk:
                return vote
        return None

    def get_rating(self):
        if self.is_relation_loaded('votes'):
            votes = self.votes.all()
            return sum(1 if vote.is_positive else -1 for vote in votes)
        return self.votes.aggregate(
            rating=Count('id', filter=Q(is_positive=True)) -
                   Count('id', filter=Q(is_positive=False))
        )['rating']


class QuestionQuerySet(models.QuerySet):
    def related_for_card(self):
        return self.select_related('user').prefetch_related('answers', 'tags', 'votes').defer('answers__text')

    def related_for_detail(self):
        return self.select_related('user').prefetch_related('answers', 'tags', 'votes', 'answers__votes',
                                                            'answers__user')


class Question(VotesModel):
    title = models.CharField(max_length=128)
    text = MartorField()
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='questions', null=True,
                             default=None)
    tags = TaggableManager(related_name='questions', through=UUIDTaggedItem)
    objects = QuestionQuerySet.as_manager()

    def has_solution(self):
        if not self.is_relation_loaded('answers'):
            return self.answers.filter(is_solution=True).exists()
        answers = self.answers.all()
        for answer in answers:
            if answer.is_solution:
                return True
        return False

    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'"{self.title}" by {self.user}'


class AnswerQuerySet(models.QuerySet):
    def related_for_card(self):
        return self.select_related('user', 'question').prefetch_related('votes').defer('question__text')


class Answer(VotesModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = MartorField()
    is_solution = models.BooleanField(default=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='answers', null=True,
                             default=None)
    objects = AnswerQuerySet.as_manager()

    class Meta:
        ordering = ['-is_solution', '-created_at']

    def get_absolute_url(self):
        return f'{self.question.get_absolute_url()}?answer_id={self.pk}'

    def __str__(self):
        return f'"{self.text[:128]}" by {self.user}'
