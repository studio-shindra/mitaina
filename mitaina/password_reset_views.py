"""パスワード リセット リダイレクト"""
from django.conf import settings
from django.shortcuts import redirect


def password_reset_redirect(request, uidb64, token):
    """パスワードリセット確認トークンをフロントエンドにリダイレクト"""
    frontend_url = f"{settings.FRONTEND_BASE_URL}/password-reset?uid={uidb64}&token={token}"
    return redirect(frontend_url)
