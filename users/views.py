from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordChangeDoneView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, RedirectView, UpdateView, DeleteView, DetailView, ListView, TemplateView

from AskAnywhere import settings
from questions_answers.models import Question, Answer
from users.forms import LoginForm, SignupUserForm, UpdateProfileForm, PasswordChangeProfileForm
from users.tokens import email_confirmation_token


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'


class SignupUser(CreateView):
    form_class = SignupUserForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:confirm_email') if settings.EMAIL_CONFIRMATION_ENABLED else reverse_lazy(
        'users:login')

    def form_valid(self, form):
        if settings.EMAIL_CONFIRMATION_ENABLED:
            user = form.instance
            user.is_active = False
            current_site = get_current_site(self.request)
            message = render_to_string('users/registration_confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'site_name': current_site.name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': email_confirmation_token.make_token(user),
                'protocol': self.request.scheme
            })
            email = EmailMessage(subject='Activate your account', body=message, to=[user.email])
            email.send()
        return super().form_valid(form)


class ConfirmEmail(TemplateView):
    template_name = 'users/confirm_email.html'


class ConfirmEmailDone(View):
    def get(self, request, uidb64, token):
        user_model = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = user_model.objects.get(pk=uid)
            if email_confirmation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return render(request, 'users/confirm_email_done.html')
            else:
                return render(request, 'users/confirm_email_invalid.html')
        except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
            return render(request, 'users/confirm_email_invalid.html')


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


class PasswordChange(PasswordChangeView):
    form_class = PasswordChangeProfileForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/change_password.html'


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'users/change_password_done.html'


class PasswordReset(PasswordResetView):
    template_name = 'users/reset_password.html'
    email_template_name = 'users/reset_password_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'users/reset_password_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'users/reset_password_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetComplete(PasswordResetCompleteView):
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
