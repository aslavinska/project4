from .models import Comment
from django import forms
from django.core.validators import EmailValidator


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.CharField(validators=[EmailValidator()])
    phone = forms.CharField(max_length=15)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)