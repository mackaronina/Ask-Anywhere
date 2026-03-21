from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import redirect, get_object_or_404
from django.template.defaultfilters import striptags
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, RedirectView
from martor.templatetags.martortags import safe_markdown

from AskAnywhere import settings
from questions_answers.forms import CreateUpdateQuestionForm, CreateUpdateAnswerForm, MarkAnswerForm, \
    SearchQuestionsForm, CreateVoteQuestionForm, CreateVoteAnswerForm
from questions_answers.models import Question, Answer, VoteQuestion, VoteAnswer
from questions_answers.utils import generate_ai_answer_text


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
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchQuestionsForm(self.request.GET)
        return context

    def get_queryset(self):
        query = Question.objects.annotate(
            answers_count=Count('answers'),
            rating=Count('votes', filter=Q(votes__is_positive=True)) -
                   Count('votes', filter=Q(votes__is_positive=False))
        )
        form = SearchQuestionsForm(self.request.GET)
        if form.is_valid():
            sort_by = form.cleaned_data['sort_by'] or 'date'
            order_by = form.cleaned_data['order_by'] or 'desc'
            has_solution = form.cleaned_data['has_solution']
            term = form.cleaned_data['term']
            tags = form.cleaned_data['tags']
            if sort_by == 'date':
                query = query.order_by('-created_at') if order_by == 'desc' else query.order_by('created_at')
            elif sort_by == 'answers':
                query = query.order_by('-answers_count') if order_by == 'desc' else query.order_by('answers_count')
            elif sort_by == 'rating':
                query = query.order_by('-rating') if order_by == 'desc' else query.order_by('rating')
            if has_solution:
                query = query.filter(answers__is_solution=True)
            if term:
                query = query.filter(Q(title__icontains=term) | Q(text__icontains=term))
            if tags:
                query = query.filter(tags__name__in=tags)
        return query.distinct().all()


class QuestionDetail(DetailView):
    model = Question
    template_name = 'questions_answers/question_detail.html'
    context_object_name = 'question'


class CreateQuestion(LoginRequiredMixin, CreateView):
    form_class = CreateUpdateQuestionForm
    template_name = 'questions_answers/create_question.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        if settings.AI_HELPER_ENABLED:
            try:
                question_text = striptags(safe_markdown(self.object.text))
                answer_text = generate_ai_answer_text(self.object.title, question_text)
                ai_user = get_user_model().objects.get(username=settings.AI_HELPER_USERNAME)
                answer = Answer(text=answer_text, user=ai_user, question=self.object)
                answer.save()
            except:
                pass
        return response


class UpdateQuestion(LoginRequiredMixin, UpdateView):
    form_class = CreateUpdateQuestionForm
    model = Question
    template_name = 'questions_answers/update_question.html'
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
        question = get_object_or_404(Question, pk=self.kwargs.get('pk'))
        context['question'] = question
        return context

    def form_valid(self, form):
        form.instance.question_id = self.kwargs.get('pk')
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateAnswer(LoginRequiredMixin, UpdateView):
    form_class = CreateUpdateAnswerForm
    model = Answer
    template_name = 'questions_answers/update_answer.html'
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


class MarkAnswer(LoginRequiredMixin, UpdateView):
    form_class = MarkAnswerForm
    model = Answer
    http_method_names = ['post']

    def get_queryset(self):
        return super().get_queryset().filter(question__user=self.request.user)


class CreateVoteQuestion(LoginRequiredMixin, CreateView):
    form_class = CreateVoteQuestionForm
    http_method_names = ['post']

    def form_valid(self, form):
        form.instance.question_id = self.kwargs.get('pk')
        form.instance.user = self.request.user
        if form.instance.question.user == form.instance.user:
            raise PermissionDenied("You can't vote for yourself")
        try:
            return super().form_valid(form)
        except IntegrityError:
            vote = get_object_or_404(VoteQuestion, question_id=self.kwargs.get('pk'), user=self.request.user)
            vote.is_positive = form.cleaned_data['is_positive']
            vote.save()
            return redirect(vote.get_absolute_url())


class DeleteVoteQuestion(LoginRequiredMixin, DeleteView):
    model = VoteQuestion
    http_method_names = ['post']

    def get_object(self, queryset=None):
        return get_object_or_404(VoteQuestion, question_id=self.kwargs.get('pk'), user=self.request.user)

    def get_success_url(self):
        return self.object.get_absolute_url()


class CreateVoteAnswer(LoginRequiredMixin, CreateView):
    form_class = CreateVoteAnswerForm
    http_method_names = ['post']

    def form_valid(self, form):
        form.instance.answer_id = self.kwargs.get('pk')
        form.instance.user = self.request.user
        if form.instance.answer.user == form.instance.user:
            raise PermissionDenied("You can't vote for yourself")
        try:
            return super().form_valid(form)
        except IntegrityError:
            vote = get_object_or_404(VoteAnswer, answer_id=self.kwargs.get('pk'), user=self.request.user)
            vote.is_positive = form.cleaned_data['is_positive']
            vote.save()
            return redirect(vote.get_absolute_url())


class DeleteVoteAnswer(LoginRequiredMixin, DeleteView):
    model = VoteAnswer
    http_method_names = ['post']

    def get_object(self, queryset=None):
        return get_object_or_404(VoteAnswer, answer_id=self.kwargs.get('pk'), user=self.request.user)

    def get_success_url(self):
        return self.object.get_absolute_url()
