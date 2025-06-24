from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/",      views.login_step1, name="login"),
    path("login/otp/",  views.login_step2, name="login_otp"),
]
