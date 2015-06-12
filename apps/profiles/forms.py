from random import choice

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

# from mongoengine.django.auth import User
from profiles.models import LabUser
from common.forms import BaseForm
from profiles.documents import TempPassword


class InviteUserForm(BaseForm):

    def __init__(self, *args, **kwargs):
        super(InviteUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].label = _('email address').capitalize()

    class Meta:
        document = LabUser
        fields = ('email',)
        using = 'mongodb'

    def save(self, commit=True):
        allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        password = ''.join([choice(allowed_chars) for i in range(10)])
        user = LabUser.create_user(self.cleaned_data['email'].replace('@', '_'), password, email=self.cleaned_data['email'])
        TempPassword(user=user, password=password).save()
        return user

    def clean_email(self):
        data = self.cleaned_data.get('email')
        try:
            LabUser.objects.get(email=data)
            raise forms.ValidationError(_("User already exist"))
        except LabUser.DoesNotExist:
            return data


class UserUpdateForm(BaseForm):

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['plot_un'].widget = forms.widgets.TextInput()
        self.fields['plot_key'].widget = forms.widgets.TextInput()

    class Meta:
        document = LabUser
        fields = ('first_name', 'last_name', 'plot_un', 'plot_key')


class ChangeUserForm(BaseForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        document = LabUser
        exclude = ('user_permissions', 'username')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email == '':
            return None
        return email


class ProfileCreationForm(BaseForm):
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"), required=False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), required=False,
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = LabUser
        fields = ('email',)
        exclude = ('user_permissions', )

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            LabUser._default_manager.get(email=email)
        except LabUser.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        self.instance.username = self.cleaned_data['username'] = self.cleaned_data.get('email', '').split('@')[0]
        user = super(ProfileCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user