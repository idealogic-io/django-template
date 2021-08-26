from django.utils import timezone
from django.db import models
import pytz
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from .managers import UserManager
import uuid


class User(AbstractBaseUser, PermissionsMixin):

    ACCOUNT_TYPES = (
        ('customer', 'customer'),
        ('enterprise', 'enterprise')
    )

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )
    name = models.CharField(
        max_length=255,
        null=True, blank=True
    )
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        choices=ACCOUNT_TYPES,
        default='customer',
        max_length=10
    )
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    welcome_email = models.BooleanField(default=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    pass_reset_date = models.DateTimeField(blank=True, null=True)
    pass_reset_code = models.CharField(max_length=20, blank=True, null=True)
    objects = UserManager()
    user_plan = models.ForeignKey('UserSubscription', on_delete=models.SET_NULL, null=True, primary_key=False, related_name='user_plan')

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name_plural = "Manage Users"
        ordering = ('-id',)

    def __str__(self):
        return self.email

    def set_password(self, raw_password, with_logout=True):
        if with_logout:
            pass
        self.password = make_password(raw_password)
        self._password = raw_password

    @staticmethod
    def callout_fee():
        return 95


class UserDevice(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='devices')
    one_signal_id = models.CharField(max_length=255, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)


class LoginSession(models.Model):
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    ended_at = models.DateTimeField(
        blank=True, null=True
    )


@receiver(post_save, sender='users.User')
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Subscription(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.CharField(max_length=255, null=False, blank=False)


class UserSubscription(models.Model):
    expiry = models.DateTimeField(null=True, blank=False)
    plan = models.ForeignKey('Subscription',on_delete=models.SET_NULL, null=True, primary_key=False, related_name='plan')


class Registration(models.Model):
    key = models.CharField(max_length=40, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=False, null=False)
    code = models.CharField(max_length=12, null=True, blank=True)
    secret_generated_at = models.DateTimeField(default=timezone.now)
    code_approved = models.BooleanField(default=False, null=True, blank=True)


class PasswordRestore(models.Model):
    key = models.CharField(max_length=40, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=False, null=False)
    code = models.CharField(max_length=12, null=True, blank=True)
    secret_generated_at = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=255)


class UserSubscriptionNotes(models.Model):
    plan = models.ForeignKey('UserSubscription', on_delete=models.CASCADE, related_name='notes')
    text = models.TextField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255, default='')
