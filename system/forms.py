from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CustomUser, OrderService, ServiceFeedback, TechnicianProfile, UserProfile
from django.contrib.auth import authenticate
# Create your forms here.


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=35, required=True)
    middle_name = forms.CharField(max_length=35, required=False)
    last_name = forms.CharField(max_length=35, required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', required=True)
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive. if you are a technician, please contact your admin."),
                code='inactive',
            )


class OrderServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderServiceForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control-plaintext'
            visible.field.widget.attrs['readonly'] = ''
            visible.field.required = False
    class Meta:
        model = OrderService
        exclude = ()

class UserProfileForm(forms.ModelForm):

    middle_name = forms.CharField(required=False)

    class Meta:
        model = UserProfile
        exclude = ('user', )

class ServiceFeedbackForm(forms.ModelForm):

    class Meta:
        model = ServiceFeedback
        exclude = ()

