# mitaina/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 表示名
    handle_name = models.CharField(max_length=50, default="")
    # username は public_id（@なしで保存、表示はフロントで @ を付ける）
    # email は一旦ユニークにしておく（後で必要になった時に使える）
    email = models.EmailField(unique=True)