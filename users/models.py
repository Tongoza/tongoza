from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import date
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError('Users must have a username')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(email, username, password, **extra_fields)


class LowercaseCharField(models.CharField):
    """
    Override CharField to convert to lowercase before saving.
    """

    def to_python(self, value):
        """
        Convert text to lowercase.
        """
        value = super(LowercaseCharField, self).to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value


class User(AbstractUser):
    username = LowercaseCharField(
        # Copying this from AbstractUser code
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator(), ],
        error_messages={
            'unique': _("A user with that dark Mode username already exists."),
        },
    )
    dark_mode_username = LowercaseCharField(
        # Copying this from AbstractUser code
        _('dark_mode_username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Required. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator(), ],
        error_messages={
            'unique': _("A user with that dark Mode username already exists."),
        },
    )
    email = models.EmailField(max_length=255, unique=True)
    phone = PhoneNumberField(blank=True, null=True)
    allow_direct_calls = models.BooleanField(default=True)
    dob = models.DateField(max_length=8, blank=True, null=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', ]

    objects = UserManager()

    def __str__(self):
        return str(self.username, )

    def get_absolute_url(self):
        return "/users/%i/" % self.pk

    def get_email(self):
        return self.email

    def has_module_perms(self, app_label):
        return True

    def calculate_age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def get_last_login(self):
        last = self.last_login
