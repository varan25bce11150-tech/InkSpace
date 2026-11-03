
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment

from .models import Post


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email",
            "class": "form-input",
        })
    )

    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "First name",
            "class": "form-input",
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Last name",
            "class": "form-input",
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "category",
            "cover_image",
            "status",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Enter your article title",
                "class": "form-input",
            }),

            "content": forms.Textarea(attrs={
                "placeholder": "Write your article here...",
                "class": "form-input",
                "rows": 12,
            }),

            "category": forms.Select(attrs={
                "class": "form-input",
            }),

            "status": forms.Select(attrs={
                "class": "form-input",
            }),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment

        fields = [
            "name",
            "email",
            "body",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Your name",
                "class": "form-input",
            }),

            "email": forms.EmailInput(attrs={
                "placeholder": "Your email",
                "class": "form-input",
            }),

            "body": forms.Textarea(attrs={
                "placeholder": "Share your thoughts...",
                "class": "form-input",
                "rows": 4,
            }),
        }

    def clean_body(self):
        body = self.cleaned_data["body"].strip()

        if len(body) < 3:
            raise forms.ValidationError(
                "Your comment must contain at least 3 characters."
            )

        return body
