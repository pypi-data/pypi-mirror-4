from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, UNUSABLE_PASSWORD

class ForgottenPasswordForm(forms.Form):
    """
    User Creation form.
    We add a few things to make this shiny.
    """
    email = forms.CharField(
        label = _("Enter your email address or username:"),
        max_length = 40,
    )
    
    def clean_email(self,):
        """
        We just check that user exists AND pwd field is accessible.
        """
        email = self.cleaned_data["email"]
        
        # Check that user exists
        # email could be username or user email
        # we always return the user email to the view
        if "@" in email:
            try:
                user = User.objects.get(email = email)
            except User.DoesNotExist:
                raise forms.ValidationError(_("This email is not registered."))
        else:
            try:
                user = User.objects.get(username = email)
            except User.DoesNotExist:
                raise forms.ValidationError(_("This username is not registered."))
        # Check that password is valid
        if user.password == UNUSABLE_PASSWORD:
            raise forms.ValidationError(_("Can't retrieve password for this user or email. Ask your system administrator."))
        return user.email

    class Meta:
        pass

class ResetPasswordForm(forms.Form):
    """
    Password reset form.
    """
    password = forms.CharField(
        label = _("Enter your new password"),
        widget=forms.PasswordInput,
    )
    confirm = forms.CharField(
        label = _("Confirm your new password"),
        help_text = _("Enter the same password as above, for verification."),
        widget=forms.PasswordInput,
    )
    
    def clean_confirm(self,):
        password = self.cleaned_data.get("password", "")
        confirm = self.cleaned_data["confirm"]
        if password != confirm:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return confirm

