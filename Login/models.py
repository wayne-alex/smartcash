from django.db import models


class Account(models.Model):
    userid = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    account_balance = models.IntegerField()
    referral_balance = models.IntegerField()
    views_balance = models.IntegerField()

    def __int__(self):
        return self.userid


class Package(models.Model):
    userid = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    package_type = models.CharField(max_length=10)
    due_date = models.DateField()


class Referral(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()  # The ID of the user who is referred (referred user)
    referrer_id = models.IntegerField()  # The ID of the user who referred someone (referrer)
    amount = models.IntegerField()


class Withdraw(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()
    amount = models.IntegerField()
    status = models.CharField(max_length=10)


class Deposit(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, default="Buy")
    user_id = models.IntegerField()
    amount = models.IntegerField()
    status = models.CharField(max_length=10)


class Mobile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()
    phone_number = models.IntegerField()
    verified = models.BooleanField(default=False)
