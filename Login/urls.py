from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('confirm_email/', views.confirm_email, name='confirm_email'),
    path('confirm-email/', views.email_confirmation, name='email_confirm'),
    path('buy_package/', views.buy_package, name='buy_package'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('withdraw-callback/', views.withdraw_callback, name='withdraw_callback'),
    path('deposit-callback/', views.deposit_callback, name='deposit_callback'),

    path('payment-status/<str:transaction_id>/', views.payment_status, name='payment_status'),

    path('phone_verification/', views.verify_phone_number, name='phone_verification'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('change-number/', views.change_number, name='change_number'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('package/', views.package, name='package'),
    path('views/', views.w_views, name='views'),
    path('bought/<str:package_type>', views.bought, name='bought'),
    path('buy/', views.package_buy, name='buy'),
    path('logout/', views.logout_user, name='logOut'),
]
