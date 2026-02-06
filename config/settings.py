from pathlib import Path
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def env(key, default=None):
    return os.environ.get(key, default)

# .env を読む（超簡易）
from dotenv import load_dotenv  # noqa
load_dotenv(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-rxer3z@2&%69%so9_bftm5k$-_bo!7a!p42h6gf#^1w(9-u=x='

SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = env("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = ["*"]

# Application definition

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "mitaina",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    "allauth.account.middleware.AccountMiddleware",

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f"postgres://{env('DB_USER','mitaina')}:{env('DB_PASSWORD','mitaina_password')}@{env('DB_HOST','127.0.0.1')}:{env('DB_PORT','5432')}/{env('DB_NAME','mitaina')}",
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "200/day",
        "user": "2000/day",
        "post_create": "10/day",
        "reaction": "300/day",
        "report": "20/day",
        "login": "30/hour",
        "dj_rest_auth": "30/hour",
    },
}

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "mitaina.serializers.RegisterSerializer",
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "mitaina.User"


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

# メール設定（開発用は console backend）
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@mitaina.local")

# フロントエンドベースURL（env化）
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", "http://localhost:5173")

# パスワードリセット設定（フロントエンドURL - env化）
PASSWORD_RESET_CONFIRM_URL = env(
    "PASSWORD_RESET_CONFIRM_URL",
    f"{FRONTEND_BASE_URL}/password-reset?uid={{uid}}&token={{token}}",
)

# dj-rest-auth設定（互換性のため両方）
REST_AUTH = {
    "PASSWORD_RESET_CONFIRM_URL": PASSWORD_RESET_CONFIRM_URL,
}
DJ_REST_AUTH = {
    "PASSWORD_RESET_CONFIRM_URL": PASSWORD_RESET_CONFIRM_URL,
}

# CORS 設定
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]

# CSRF 信頼オリジン
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]

REST_AUTH = {"PASSWORD_RESET_CONFIRM_URL": PASSWORD_RESET_CONFIRM_URL}
DJ_REST_AUTH = {"PASSWORD_RESET_CONFIRM_URL": PASSWORD_RESET_CONFIRM_URL}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"