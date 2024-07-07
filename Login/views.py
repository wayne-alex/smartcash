from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Account, Package, Profile, Affiliate, EmailToken


# Helping methods
def mask_email(email):
    # Split the email into username and domain parts
    username, domain = email.split('@')
    # Mask the username part
    masked_username = username[:2] + '*****' + username[-1:]
    # Combine the masked username with the domain
    return masked_username + '@' + domain


def send_email(name, to, subject, html_message):
    url = "https://node-mailer-brown.vercel.app/send-email"
    email_data = {
        "name": name,
        "to": to,
        "subject": subject,
        "html_message": html_message,
    }
    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=email_data, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error:", e)


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


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone_number = request.POST.get('phone_number')
        invited_by = request.POST.get('invited_by')
        if not username or not email or not password or not confirm_password or not phone_number:
            messages.error(request, 'All fields are required.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(profile__phone_number=phone_number).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('register')  # Replace with your register URL

        # Create User object
        user = User.objects.create_user(username=username, email=email, password=password)
        acc = Account.objects.create(user=user, )
        _profile = Profile(user=user, phone_number=phone_number)
        _profile.save()
        referrer_username = invited_by
        if referrer_username:
            try:
                referrer_user = User.objects.get(username=referrer_username)
                Affiliate.objects.create(user=user, referer=referrer_user)
            except User.DoesNotExist:
                referrer_user = None

        messages.success(request,
                         "You have successfully registered! Kindly confirm your Email Address to continue.")
        return redirect('confirm_email')
    else:
        aff = request.GET.get('aff')
        if aff:
            return render(request, 'register.html', {'aff': aff})
    return render(request, 'register.html')


@login_required
def confirm_email(request):
    user = request.user
    acc = Account.objects.get(user=user)
    email_state = acc.email_confirmed

    # If email is already confirmed, redirect to dashboard
    if email_state:
        return redirect('dashboard')
    else:
        recent_email_token = EmailToken.objects.filter(user=user,
                                                       created_at__gte=timezone.now() - timedelta(minutes=20)).exists()

        # If there's a recent token, inform the user and render the same page
        if recent_email_token:
            messages.success(request, 'Email already sent to your email address')
            return render(request, 'confirm_email.html',
                          {'email': mask_email(user.email), 'reason': 'Confirm your Email Address'})
        else:
            eT = EmailToken(user=user)
            eT.save()
            recent_email_token = EmailToken.objects.filter(user=user, created_at__gte=timezone.now() - timedelta(
                minutes=20)).first()

            _token = recent_email_token.token
            # Generate the confirmation URL
            confirm_url = f"https://smartcash.vercel.app/confirm-email/?token={_token}"

            # Send the confirmation email
            email = user.email
            name = 'SMARTCASH LTD'
            subject = 'Confirm Email'
            send_email(
                name=name,
                subject=subject,
                to=email,
                html_message=render_to_string('confirmEmail.html',
                                              {'username': user.username, 'confirm_url': confirm_url})
            )
            messages.info(request, 'An email has been sent to confirm your email address.')

            return render(request, 'confirm_email.html',
                          {'email': mask_email(email), 'reason': 'Confirm your Email Address'})


def email_confirmation(request):
    token = request.GET.get('token')

    if token:
        # Check if the token exists and is valid
        email_token = get_object_or_404(EmailToken, token=token, created_at__gte=timezone.now() - timedelta(hours=24))
        user = email_token.user

        # Mark email as confirmed
        acc = get_object_or_404(Account, user=user)
        acc.email_confirmed = True
        acc.save()

        # Delete the email token after it has been used for confirmation
        email_token.delete()

        # Redirect to some page after successful confirmation
        messages.success(request, 'Your email has been successfully confirmed.')
        email = user.email
        name = 'SMARTCASH LTD'
        subject = 'Welcome to Smart Cash'
        url = f"https://smartcash.vercel.app/login"
        send_email(
            to=email, name=name, subject=subject,
            html_message=render_to_string('welcomeEmail.html', {'name': user.username, 'url': url})
        )
        return redirect('dashboard')  # Redirect to dashboard or any other page

    else:
        # Handle case where token is missing or invalid
        messages.error(request, 'Invalid or expired confirmation link.')
        return redirect('login')  # Redirect to login page or handle as appropriate


@login_required()
def dashboard(request):
    user = request.user
    acc = Account.objects.get(user=user)
    buy_state = acc.package_bought

    if not buy_state:
        return redirect('buy_package')


@login_required
def dashboard(request):
    username = request.user.username
    user_id = request.user.id
    account = Account.objects.get(userid=user_id)
    package_ = Package.objects.get(userid=user_id)

    return render(request, 'dashboard.html', {'username': username, 'account': account, 'package': package_})


@login_required()
def buy_package(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    phone = profile.phone_number
    acc = Account.objects.get(user=user)
    if acc.package_bought:
        return redirect('dashboard')
    else:
        return render(request, 'buy_package.html', {'phone': phone})


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
