import uuid
import sys
from io import BytesIO
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


class User(AbstractUser):

    """ Custom User Model """

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"

    GENDER_CHOICES = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
        (GENDER_OTHER, _("Other")),
    )

    LANGUAGE_ENGLISH = "en"
    LANGUAGE_KOREAN = "ko"

    LANGUAGE_CHOICES = (
        (LANGUAGE_ENGLISH, _("English")),
        (LANGUAGE_KOREAN, _("Korean")),
    )

    CURRENCY_USD = "usd"
    CURRENCY_KRW = "krw"

    CURRENCY_CHOICES = ((CURRENCY_USD, "USD"), (CURRENCY_KRW, "KRW"))

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_KAKAO = "kakao"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, _("Email")),
        (LOGIN_GITHUB, _("Github")),
        (LOGIN_KAKAO, _("Kakao")),
    )

    avatar = models.ImageField(upload_to="avatars/", blank=True)
    gender = models.CharField(choices=GENDER_CHOICES,
                              max_length=10, blank=True)
    bio = models.TextField(default="", blank=True)
    birthdate = models.DateField(null=True)
    language = models.CharField(
        choices=LANGUAGE_CHOICES, max_length=2, blank=True)
    currency = models.CharField(
        choices=CURRENCY_CHOICES, max_length=3, blank=True)
    superhost = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_secret = models.CharField(
        max_length=120, default="", blank=True, null=True)
    login_method = models.CharField(
        max_length=50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL)

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={'pk': self.pk})

    def verify_email(self):
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20]
            self.email_secret = secret
            html_message = render_to_string(
                "emails/verify_email.html", {'secret': secret})
            send_mail(
                _("Verify Airbnb Account"),
                strip_tags(html_message),
                settings.EMAIL_FROM,
                [self.email, ],
                fail_silently=True,
                html_message=html_message,
            )
            self.save()
