from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from martor.fields import MartorFormField
from martor.widgets import MartorWidget
from taggit.forms import TagField, TagWidget

from questions_answers.models import Question, Answer, Vote


class CreateUpdateQuestionForm(forms.ModelForm):
    title = forms.CharField(min_length=5, max_length=128, label=_('Question title'), widget=forms.TextInput(
        attrs={'placeholder': _('Enter your question here. The question must end with a question mark')}))
    text = MartorFormField(min_length=5, max_length=8192, label=_('Question body'), widget=MartorWidget(
        attrs={'placeholder': _('Describe your question in detail so that everyone understands')}))
    tags = TagField(required=False, max_length=128, label=_('Tags'), widget=TagWidget(
        attrs={'placeholder': _('Provide a comma-separated list of tags (optional)')}))

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']

    def clean_title(self):
        title = self.cleaned_data['title']
        if title[-1] != '?':
            raise ValidationError(_('The question title must end with a question mark'))
        return title


class CreateUpdateAnswerForm(forms.ModelForm):
    text = MartorFormField(min_length=5, max_length=8192, label=_('Answer body'), widget=MartorWidget(
        attrs={'placeholder': _('Write a detailed answer to the question. Avoid repeating other answers')}))

    class Meta:
        model = Answer
        fields = ['text']


class MarkAnswerForm(forms.ModelForm):
    is_solution = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Answer
        fields = ['is_solution']


class CreateVoteForm(forms.ModelForm):
    is_positive = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Vote
        fields = ['is_positive']


class SearchQuestionsForm(forms.Form):
    SORT_CHOICES = [
        ('date', _('Creation date')),
        ('answers', _('Answers count')),
        ('rating', _('Rating'))
    ]
    ORDER_CHOICES = [
        ('desc', _('Descending')),
        ('asc', _('Ascending'))
    ]
    term = forms.CharField(label='', min_length=3, max_length=128, required=False,
                           widget=forms.TextInput(attrs={'placeholder': _('Search...')}))
    sort_by = forms.ChoiceField(label=_('Sort by'), choices=SORT_CHOICES, widget=forms.Select(), required=False,
                                initial='date')
    order_by = forms.ChoiceField(label=_('Order by'), choices=ORDER_CHOICES, widget=forms.Select(), required=False,
                                 initial='desc')
    tags = TagField(required=False, max_length=128, label=_('Tags'), widget=TagWidget(
        attrs={'placeholder': _('Comma-separated list of tags')}))
    has_solution = forms.BooleanField(label=_('Only questions with solution'), required=False)
