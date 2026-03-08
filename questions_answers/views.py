from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, RedirectView

from questions_answers.forms import CreateUpdateQuestionForm, CreateUpdateAnswerForm, MarkAnswerForm
from questions_answers.models import Question, Answer


class Index(ListView):
    model = Question
    template_name = 'questions_answers/index.html'
    context_object_name = 'recent'

    def get_queryset(self):
        queryset = {
            'questions': Question.objects.order_by('-created_at')[:5],
            'answers': Answer.objects.order_by('-created_at')[:5]
        }
        return queryset


class QuestionsIndex(ListView):
    model = Question
    template_name = 'questions_answers/questions_index.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.order_by('-created_at').all()


class QuestionDetail(DetailView):
    model = Question
    template_name = 'questions_answers/question_detail.html'
    context_object_name = 'question'
    extra_context = {
        'mark_answer_form': MarkAnswerForm(initial={'is_solution': True}),
        'unmark_answer_form': MarkAnswerForm(initial={'is_solution': False}),
    }


class CreateQuestion(LoginRequiredMixin, CreateView):
    form_class = CreateUpdateQuestionForm
    template_name = 'questions_answers/create_question.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateQuestion(LoginRequiredMixin, UpdateView):
    form_class = CreateUpdateQuestionForm
    template_name = 'questions_answers/update_question.html'
    model = Question
    context_object_name = 'question'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class DeleteQuestion(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('index')
    extra_context = {
        'entity_name': 'your question'
    }

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class RandomQuestion(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        random_question = Question.objects.order_by('?').first()
        if random_question is None:
            return reverse('questions_index')
        return random_question.get_absolute_url()


class CreateAnswer(LoginRequiredMixin, CreateView):
    form_class = CreateUpdateAnswerForm
    template_name = 'questions_answers/create_answer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = get_object_or_404(Question, pk=self.kwargs.get('question_id'))
        context['question'] = question
        return context

    def form_valid(self, form):
        form.instance.question_id = self.kwargs.get('question_id')
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateAnswer(LoginRequiredMixin, UpdateView):
    form_class = CreateUpdateAnswerForm
    template_name = 'questions_answers/update_answer.html'
    model = Answer
    context_object_name = 'answer'

    def form_valid(self, form):
        if form.instance.is_solution:
            raise ValidationError('Answer marked as solution cannot be modified')
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class DeleteAnswer(LoginRequiredMixin, DeleteView):
    model = Answer
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('index')
    extra_context = {
        'entity_name': 'your answer'
    }

    def form_valid(self, form):
        if form.instance.is_solution:
            raise ValidationError('Answer marked as solution cannot be modified')
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MarkAnswer(LoginRequiredMixin, View):
    def post(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        if answer.question.user != request.user:
            raise PermissionDenied()
        form = MarkAnswerForm(request.POST)
        if form.is_valid():
            answer.is_solution = form.cleaned_data.get('is_solution')
            answer.save()
            return redirect(answer.get_absolute_url())
        else:
            raise ValidationError(form.errors)
