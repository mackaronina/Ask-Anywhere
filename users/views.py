from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, DetailView

from users.forms import LoginForm, SignupUserForm, UpdateProfileForm


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'


class SignupUser(CreateView):
    form_class = SignupUserForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')


class ProfileDetail(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UpdateProfileForm
    template_name = 'users/update_profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


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

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.pk == kwargs['pk']:
            return redirect(reverse('users:profile'))
        return super().get(request, *args, **kwargs)
