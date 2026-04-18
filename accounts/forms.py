from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter a strong password"}),
        help_text="",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Re-enter your password"}),
        help_text="",
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        }
        help_texts = {
            "username": "",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            try:
                validate_password(password, user=None)
            except ValidationError as e:
                custom_errors = []
                for error in e.messages:
                    if "8 characters" in error or "minimum length" in error.lower():
                        custom_errors.append("Password must be at least 8 characters")
                    elif "similar" in error.lower() or "username" in error.lower() or "attribute" in error.lower():
                        custom_errors.append("Password should not be similar to your email or username")
                    else:
                        custom_errors.append(error)
                
                seen = set()
                unique_errors = []
                for err in custom_errors:
                    if err not in seen:
                        unique_errors.append(err)
                        seen.add(err)
                
                raise forms.ValidationError(unique_errors)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match. Please try again.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_STUDENT
        if commit:
            user.save()
        return user
