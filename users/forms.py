from django import forms
from users.models import User
from tongozahome.models import Profile, ProfileImage
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from django.utils.translation import gettext_lazy as _

GENDER_ROLES = {
    ('M', 'Male'),
    ('F', 'Female'),
}

SEXUAL_ORIENTATION = {
    ('Bi', 'Bisexual'),
    ('St', 'Straight'),
}


class UserUpdateForm(forms.ModelForm):
    phone = forms.CharField(required=True, widget=PhoneNumberPrefixWidget(initial='RW', attrs={
        'placeholder': 'Phone Number',
        'class': 'form-control form-control-alternative',

    }))

    dob = forms.CharField(required=True, widget=forms.DateInput(attrs={
        'class': 'form-control form-control-alternative',
        'placeholder': 'YYYY-MM-DD i.e 1996-08-18'

    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'dob', 'phone', 'allow_direct_calls')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-alternative',
                'placeholder': 'Change Username'

            }),

            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-alternative',
                'placeholder': 'First Name'

            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-alternative',
                'placeholder': 'Last Name'

            }),

        }

    # def clean_email(self):
    #     email = self.cleaned_data['email'].lower()
    #     try:
    #         account = User.objects.exclude(pk=self.instance.pk).get(email=email)
    #     except User.DoesNotExist:
    #         return email
    #     if email != account.email:
    #         raise forms.ValidationError('Email "%s" is already in use.' % email)
    #
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        try:
            account = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username

        if not username == account.username:
            raise forms.ValidationError('Username "%s" is already in use.' % username)

    # def clean_phone(self):
    #     phone = self.cleaned_data['phone']
    #     if phone is not None:
    #         try:
    #             account = User.objects.exclude(pk=self.instance.pk).get(phone=phone)
    #
    #         except User.DoesNotExist:
    #             return phone
    #
    #         if phone == account.phone:
    #             raise forms.ValidationError('Phone number "%s" is already in use.' % phone)
    #
    def save(self, commit=True):
        account = super(UserUpdateForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        # account.email = self.cleaned_data['email'].lower()
        # account.phone = self.cleaned_data['phone']
        if commit:
            account.save()
        return account


class ProfileUpdateForm(forms.ModelForm):
    aboutMe = forms.CharField(max_length=300, required=True, widget=forms.Textarea(attrs={
        'class': 'form-control form-control-alternative',
        'placeholder': 'Write something interesting about you'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-control-alternative',
        }))
    city = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-alternative',
        'placeholder': 'Kigali'
    }))
    whatsapp_phone_number = forms.CharField(required=False, widget=PhoneNumberPrefixWidget(initial='KE', attrs={
        'placeholder': 'Number(optional)',
        'class': 'form-control form-control-alternative',

    }))
    telegram_username = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Username(optional)',
        'class': 'form-control form-control-alternative',

    }))
    snapchat_username = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Username(optional)',
        'class': 'form-control form-control-alternative',

    }))
    messenger = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Page name(optional)',
        'class': 'form-control form-control-alternative',

    }))
    education_institution = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'College (optional)',
        'class': 'form-control form-control-alternative',

    }))
    course = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Course(optional)',
        'class': 'form-control form-control-alternative',

    }))
    company = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Name(optional)',
        'class': 'form-control form-control-alternative',

    }))
    role = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Role(optional)',
        'class': 'form-control form-control-alternative',

    }))

    gender = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=GENDER_ROLES)

    # sexual_orientation = forms.ChoiceField(
    #     widget=forms.RadioSelect(),
    #     choices=SEXUAL_ORIENTATION)

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user', 'address', 'postal_code')

        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-alternative',
                'placeholder': 'KG 658 ST, Kacyiru'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control form-control-alternative',
                'placeholder': '00100'
            }),
        }

    # def clean_whatsapp_phone_number(self):
    #     whatsapp_phone_number = self.cleaned_data['whatsapp_phone_number']
    #
    #     if whatsapp_phone_number is not None:
    #         try:
    #             profile = Profile.objects.exclude(user=self.instance.pk).get(
    #                 whatsapp_phone_number=whatsapp_phone_number)
    #
    #         except Profile.DoesNotExist:
    #             return whatsapp_phone_number
    #
    #         if whatsapp_phone_number == profile.whatsapp_phone_number:
    #             raise forms.ValidationError(
    #                 'This Whatsapp Phone number "%s" is already in use.' % whatsapp_phone_number)
    #
    # def save(self, commit=True):
    #     profile = super(ProfileUpdateForm, self).save(commit=False)
    #     profile.whatsapp_phone_number = self.cleaned_data['whatsapp_phone_number']
    #     if commit:
    #         profile.save()
    #     return profile


class ProfileUpdateImageForm(forms.ModelForm):
    class Meta:
        model = ProfileImage
        fields = ('image',)
        # exclude = ('profile', 'dark_profile', 'dark_mode_pic', 'caption','profile_pic')

        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-control form-control-alternative',
            }),

        }
