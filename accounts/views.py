from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from .utils import send_email_otp
from .models import EmailOTP
from django.conf import settings

def login_step1(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            send_email_otp(user)
            request.session["preauth_user_id"] = user.id
            return redirect("accounts:login_otp")
        messages.error(request, "Identifiant ou mot de passe incorrect.")
    return render(request, "accounts/login_step1.html")

def login_step2(request):
    user_id = request.session.get("preauth_user_id")
    if not user_id:
        return redirect("accounts:login")
    if request.method == "POST":
        code = request.POST.get("otp_code")
        otp_qs = EmailOTP.objects.filter(user_id=user_id, code=code) \
                                 .order_by("-created_at")
        if otp_qs and not otp_qs.first().is_expired():
            user = otp_qs.first().user
            auth_login(request, user)
            return redirect("dashboard")
        messages.error(request, "Code invalide ou expiré.")
    return render(request, "accounts/login_step2.html")
