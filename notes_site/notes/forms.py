from django import forms
from .models import Note
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .utils import load_priorities
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class SigninForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите учётную запись или почтовый адрес',
            'autocomplete': "off"
        }),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'autocomplete': "off"
        }),
    )

class NoteForm(forms.ModelForm):
    title = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter title (optional)'})
    )
    text = forms.CharField(
        max_length=10000,
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Enter text'}),
    )
    priority = forms.ChoiceField(
        choices=load_priorities(),
        initial=1,
        widget=forms.Select(),
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Note
        fields = ['title', 'text', 'priority', 'due_date']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title', '').strip()
        text = cleaned_data.get('text', '').strip()

        if not title and not text:
            raise ValidationError(_('Either title or text must be provided.'))

        return cleaned_data

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']