import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default=False)
    package_bought = models.BooleanField(default=False)
    account_balance = models.IntegerField()
    referral_balance = models.IntegerField()
    views_balance = models.IntegerField()

    def __str__(self):
        return f"Account(user={self.user.username}, email_confirmed={self.email_confirmed}, package_bought={self.package_bought})"


class Package(models.Model):
    name = models.CharField(max_length=255,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    def __str__(self):
        return self.name


class Affiliate(models.Model):
    user = models.OneToOneField(User, related_name='affiliate', on_delete=models.CASCADE)
    referer = models.ForeignKey(User, related_name='referred_user', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    verified = models.BooleanField(default=False)


class Withdraw(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=10)


class Deposit(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, default="Buy")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=10)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, unique=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


class EmailToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmailToken(user={self.user}, token={self.token})"
