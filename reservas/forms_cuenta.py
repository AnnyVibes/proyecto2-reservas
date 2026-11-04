"""Formulario de registro de clientes."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', max_length=254,
                             error_messages={'invalid': 'Escribe un correo electrónico válido.'})
    first_name = forms.CharField(label='Nombre', max_length=150)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
        labels = {'username': 'Usuario'}
        help_texts = {'username': 'Hasta 150 caracteres: letras, números y @ . + - _'}

    def clean_first_name(self):
        nombre = self.cleaned_data['first_name'].strip()
        if not nombre:
            raise forms.ValidationError('Escribe tu nombre.')
        return nombre

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email
