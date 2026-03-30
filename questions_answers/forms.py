from django import forms
from django.core.exceptions import ValidationError
from martor.fields import MartorFormField
from martor.widgets import MartorWidget
from taggit.forms import TagField, TagWidget

from questions_answers.models import Question, Answer, Vote


class CreateUpdateQuestionForm(forms.ModelForm):
    title = forms.CharField(min_length=5, max_length=128, label='Question title', widget=forms.TextInput(
        attrs={'placeholder': 'Enter your question here. The question must end with a question mark'}))
    text = MartorFormField(min_length=5, max_length=8192, label='Question body', widget=MartorWidget(
        attrs={'placeholder': 'Describe your question in detail so that everyone understands'}))
    tags = TagField(required=False, max_length=128, label='Tags', widget=TagWidget(
        attrs={'placeholder': 'Provide a comma-separated list of tags (optional)'}))

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']

    def clean_title(self):
        title = self.cleaned_data['title']
        if title[-1] != '?':
            raise ValidationError('The question title must end with a question mark')
        return title


class CreateUpdateAnswerForm(forms.ModelForm):
    text = MartorFormField(min_length=5, max_length=8192, label='Answer body', widget=MartorWidget(
        attrs={'placeholder': 'Write a detailed answer to the question. Avoid repeating other answers'}))

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
        ('date', 'Creation date'),
        ('answers', 'Answers count'),
        ('rating', 'Rating')
    ]
    ORDER_CHOICES = [
        ('desc', 'Descending'),
        ('asc', 'Ascending')
    ]
    term = forms.CharField(label='', min_length=3, max_length=128, required=False,
                           widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
    sort_by = forms.ChoiceField(label='Sort by', choices=SORT_CHOICES, widget=forms.Select(), required=False,
                                initial='date')
    order_by = forms.ChoiceField(label='Order by', choices=ORDER_CHOICES, widget=forms.Select(), required=False,
                                 initial='desc')
    tags = TagField(required=False, max_length=128, label='Tags', widget=TagWidget(
        attrs={'placeholder': 'Comma-separated list of tags to search'}))
    has_solution = forms.BooleanField(label='Only questions with solution', required=False)
