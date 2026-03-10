from django import forms
from django.core.exceptions import ValidationError

from questions_answers.models import Question, Answer


class CreateUpdateQuestionForm(forms.ModelForm):
    title = forms.CharField(min_length=5, max_length=128, label='Question title',
                            empty_value='Enter your question here. The question must end with a question mark')
    text = forms.CharField(min_length=5, max_length=4096, widget=forms.Textarea(), label='Question body',
                           empty_value='Describe your question in detail so that everyone understands')

    class Meta:
        model = Question
        fields = ['title', 'text']

    def clean_title(self):
        title = self.cleaned_data['title']
        if title[-1] != '?':
            raise ValidationError('The question title must end with a question mark')
        return title


class CreateUpdateAnswerForm(forms.ModelForm):
    text = forms.CharField(min_length=5, max_length=4096, widget=forms.Textarea(), label='Answer body',
                           empty_value='Describe your question in detail so that everyone understands')

    class Meta:
        model = Answer
        fields = ['text']


class MarkAnswerForm(forms.Form):
    is_solution = forms.BooleanField(widget=forms.HiddenInput(), required=False)


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
    sort_by = forms.ChoiceField(label='Sort by', choices=SORT_CHOICES, widget=forms.Select(), required=False)
    order_by = forms.ChoiceField(label='Order by', choices=ORDER_CHOICES, widget=forms.Select(), required=False)
    has_solution = forms.BooleanField(label='Only questions with solution', required=False)
