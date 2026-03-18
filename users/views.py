from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordChangeDoneView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, RedirectView, UpdateView, DeleteView, DetailView, ListView

from questions_answers.models import Question, Answer
from users.forms import LoginForm, SignupUserForm, UpdateProfileForm, PasswordChangeProfileForm


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'


class SignupUser(CreateView):
    form_class = SignupUserForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')


class ProfileDetail(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('users:user_detail', kwargs={'pk': self.request.user.pk})


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UpdateProfileForm
    template_name = 'users/update_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChangeProfile(PasswordChangeView):
    form_class = PasswordChangeProfileForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/change_password.html'


class PasswordChangeDoneProfile(PasswordChangeDoneView):
    template_name = 'users/change_password_done.html'


class PasswordResetProfile(PasswordResetView):
    template_name = 'users/reset_password.html'
    email_template_name = 'users/reset_password_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDoneProfile(PasswordResetDoneView):
    template_name = 'users/reset_password_done.html'


class PasswordResetConfirmProfile(PasswordResetConfirmView):
    template_name = 'users/reset_password_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetCompleteProfile(PasswordResetCompleteView):
    template_name = 'users/reset_password_complete.html'


class DeleteProfile(LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('index')
    extra_context = {
        'entity_name': 'your account'
    }

    def get_object(self, queryset=None):
        return self.request.user


class UserDetail(DetailView):
    model = get_user_model()
    template_name = 'users/user_detail.html'
    context_object_name = 'user_object'


class UserQuestionsList(ListView):
    model = Question
    template_name = 'users/user_questions_list.html'
    context_object_name = 'questions'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_object'] = get_object_or_404(get_user_model(), pk=self.kwargs.get('pk'))
        return context

    def get_queryset(self):
        return Question.objects.filter(user_id=self.kwargs.get('pk')).order_by('-created_at').all()


class UserAnswersList(ListView):
    model = Answer
    template_name = 'users/user_answers_list.html'
    context_object_name = 'answers'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_object'] = get_object_or_404(get_user_model(), pk=self.kwargs.get('pk'))
        return context

    def get_queryset(self):
        return Answer.objects.filter(user_id=self.kwargs.get('pk')).order_by('-created_at').all()
