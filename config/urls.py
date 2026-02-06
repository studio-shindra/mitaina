# config/urls.py
from django.contrib import admin
from django.urls import path, include
from mitaina.views import password_reset_redirect

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/", include("mitaina.urls")),

    # パスワードリセットリダイレクト（A案：django.contrib.auth.urlsより前に定義）
    path("accounts/reset/<uidb64>/<token>/", password_reset_redirect, name="password_reset_confirm"),

    # Django標準のパスワードリセットURL（reverse用）
    path("accounts/", include("django.contrib.auth.urls")),
]