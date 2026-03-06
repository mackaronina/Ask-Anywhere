from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or e-mail')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class SignupUserForm(UserCreationForm):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use')
        return email


class UpdateProfileForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    email = forms.EmailField(disabled=True, label='E-mail')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']
