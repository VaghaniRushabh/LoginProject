from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from users.manager import UserManager
# Create your models here.

class CustomUser(AbstractUser):
    username = None
    user_name = models.CharField(
        _("User Name"),
        max_length=255,
        unique=True,
        null=True,
        blank=False,
        error_messages={"unique": "This username is already excited"},
    )
    email = models.EmailField(
        _("Email"),
        max_length=255,
        unique=True,
        null=True,
        blank=False,
        error_messages={"unique": "This email is already excited."},
    )
    phone = PhoneNumberField(
        _("Phone No."),
        help_text="Provide a number with country code (e.g. +12125552368).",
        null=True,
        blank=False,
    )
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_admin(self):
        return self.is_superuser

    def get_absolute_url(self):
        return reverse("users:users")



class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
