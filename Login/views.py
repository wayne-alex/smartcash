from datetime import datetime, timedelta

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Account, Package, Referral,Mobile
from django.urls import reverse
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required


def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully signed in")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error while signing in")
            return redirect('home')
    else:
        return render(request, 'home.html')


def register_user(request, referrer):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            # Retrieve the referrer user based on the referrer parameter (assuming referrer is the username)
            try:
                referrer_user = User.objects.get(username=referrer)
            except User.DoesNotExist:
                # Handle the case where the referrer user does not exist
                referrer_user = None
            messages.success(request, "You have successfully registered! Choose a preferred package to continue")
            user_id = request.user.id
            # Create or update the Account and Referral objects for the user
            acc, _ = Account.objects.get_or_create(userid=user_id,
                                                   defaults={'account_balance': 0, 'referral_balance': 0,
                                                             'views_balance': 0})
            if referrer_user:
                ref, _ = Referral.objects.get_or_create(user_id=user_id, referrer_id=referrer_user.id,
                                                        defaults={'amount': 0})
            return redirect('phone_verification')

    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    username = request.user.username
    user_id = request.user.id
    account = Account.objects.get(userid=user_id)
    package_ = Package.objects.get(userid=user_id)

    return render(request, 'dashboard.html', {'username': username, 'account': account, 'package': package_})


@login_required
def w_views(request):
    username = request.user.username
    user_id = request.user.id
    account = Account.objects.get(userid=user_id)
    package_ = Package.objects.get(userid=user_id)
    referral_count = Referral.objects.filter(referrer_id=user_id).count()
    print("Referral count:", referral_count)

    return render(request, 'w_views.html',
                  {'username': username, 'account': account, 'package': package_, 'referral_count': referral_count})


@login_required
def package(request):
    username = request.user.username
    return render(request, 'package.html', {'username': username})


def package_buy(request):
    return render(request, 'package_buy.html')


def buy_package(request, username, package_type):
    username = username
    package_type = package_type

    return render(request, 'buy.html', {'username': username, 'package_type': package_type})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home')


def bought(request, package_type):
    package_type = package_type
    user_id = request.user.id

    # Calculate the due date (now + 30 days)
    due_date = datetime.now() + timedelta(days=30)

    x = Package(userid=user_id, package_type=package_type, due_date=due_date)
    x.save()

    y = Referral.objects.get(user_id=user_id)
    referrer_id = y.referrer_id
    if package_type == 'GOLD':
        y.amount = 500
    elif package_type == 'SILVER':
        y.amount = 200
    else:
        y.amount = 100
    y.save()

    z = Account.objects.get(userid=referrer_id)
    a = Package.objects.get(userid=user_id)
    referrer_package = a.package_type

    if referrer_package == 'GOLD':
        if package_type == 'GOLD':
            z.referral_balance = 175
        elif package_type == 'SILVER':
            z.referral_balance = 70
        else:
            z.referral_balance = 35
    elif referrer_package == 'SILVER':
        if package_type == 'GOLD':
            z.referral_balance = 100
        elif package_type == 'SILVER':
            z.referral_balance = 40
        else:
            z.referral_balance = 20
    else:
        if package_type == 'GOLD':
            z.referral_balance = 50
        elif package_type == 'SILVER':
            z.referral_balance = 20
        else:
            z.referral_balance = 10
    z.save()

    messages.success(request, "Successfully purchased " + package_type)
    return redirect('dashboard')


@login_required
def verify_phone_number(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        url = 'http://13.51.196.90:3000/trigger-function'
        payload = {'phone_number': phone}
        user_id = request.user.id
        verified = False
        # Check if the phone number is already associated with another user
        try:
            mobile = Mobile.objects.get(phone_number=phone)
            if mobile.user_id != user_id:
                messages.error(request,
                               'The phone number is already in use by another user. Please try another number.')
                return render(request, 'mobile.html', {'verification_code_sent': False})
        except Mobile.DoesNotExist:
            # If the phone number is not associated with any user, create a new account
            mobile = Mobile(user_id=user_id, phone_number=phone, verified=verified)
            mobile.save()

        # If the phone number is associated with the current user or not associated with any user, continue with sending the verification code
        try:
            response = requests.get(url, params=payload)
            response.raise_for_status()
            code = response.text.replace('Message successfully sent. Verification code is: ', '')

            # Store the code in the session
            request.session['verification_code'] = code

            return render(request, 'mobile.html', {'verification_code_sent': True})

        except requests.exceptions.RequestException as e:
            messages.error(request, 'Error while sending the verification code.')
            print(f"Error: {e}")
            return render(request, 'mobile.html', {'verification_code_sent': False})

    else:
        return render(request, 'mobile.html', {'verification_code_sent': False})

@login_required
def verify_code(request):
    if request.method == 'POST':
        # Retrieve the code from the session
        code = request.session.get('verification_code', None)
        if not code:
            # Handle the case where the code is not found in the session
            # Redirect or show an error message, etc.
            return redirect('verify_phone_number')

        # Process the code and check if it matches the user input.
        user_input_code = request.POST.get('verification_code')
        if code == user_input_code:
            messages.success(request, "Phone number successfully Verified")
            account = Mobile.objects.get(user_id=request.user.id)
            account.verified = True
            account.save()
            username = request.user.username
            return render(request, 'package_buy.html',
                          {'username': username})  # Redirect to the appropriate URL for package selection
        else:
            # Code is incorrect, display an error message, or redirect back to the verification page.
            messages.success(request, "Verification code entered is incorrect.")
            logout(request)
            return redirect('phone_verification')

    else:
        return redirect('verify_phone_number')



def resend_code(request):
    # Code to resend the verification code goes here.
    return redirect('verify_phone_number')


def change_number(request):
    # Code to allow the user to change their phone number goes here.
    return redirect('verify_phone_number')