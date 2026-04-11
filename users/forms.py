from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username or e-mail'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput())


class SignupUserForm(UserCreationForm):
    username = forms.CharField(label=_('Username'))
    email = forms.EmailField(label=_('E-mail'))
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput())
    password2 = forms.CharField(label=_('Repeat password'), widget=forms.PasswordInput())
    captcha = CaptchaField(label=_('Captcha'), widget=CaptchaTextInput(
        attrs={'placeholder': _('Type the characters from the image above')}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email is already in use'))
        return email


class UpdateProfileForm(forms.ModelForm):
    username = forms.CharField(label=_('Username'))
    email = forms.EmailField(label=_('E-mail'), disabled=True)
    photo = forms.ImageField(
        label=_('Profile avatar'),
        required=False,
        validators=[FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg', 'gif', 'webp']
        )]
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class PasswordChangeProfileForm(PasswordChangeForm):
    old_password = forms.CharField(label=_('Old password'), widget=forms.PasswordInput())
    new_password1 = forms.CharField(label=_('New password'), widget=forms.PasswordInput())
    new_password2 = forms.CharField(label=_('Repeat password'), widget=forms.PasswordInput())
