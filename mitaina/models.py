# mitaina/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils import timezone


class User(AbstractUser):
    # 表示名
    handle_name = models.CharField(max_length=50, default="")
    # username は public_id（@なしで保存、表示はフロントで @ を付ける）
    # email は一旦ユニークにしておく（後で必要になった時に使える）
    email = models.EmailField(unique=True)


class Post(models.Model):
    """投稿モデル"""
    GENRE_CHOICES = [
        ("stage", "stage"),
        ("movie", "movie"),
        ("novel", "novel"),
        ("anime", "anime"),
        ("manga", "manga"),
        ("other", "other"),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.CharField(max_length=141)  # 「みたいな」はまだ付与していない
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    work_title = models.CharField(max_length=141, blank=True, null=True)
    performer_name = models.CharField(max_length=141, blank=True, null=True)
    character_name = models.CharField(max_length=141, blank=True, default="")

    # カウンタキャッシュ
    like_count = models.PositiveIntegerField(default=0)
    hatena_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # 論理削除

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.handle_name}: {self.text[:50]}"


class Reaction(models.Model):
    """リアクションモデル"""
    TYPE_CHOICES = [
        ("like", "👍みたい"),
        ("hatena", "❓いやちゃうやろw"),
        ("correct", "🚫これは正確な引用です"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    reaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post", "reaction_type")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.handle_name} - {self.reaction_type} on {self.post.id}"


class Follow(models.Model):
    """フォローモデル"""
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following_list"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers_list"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def clean(self):
        """自分自身をフォローできないようにバリデーション"""
        from django.core.exceptions import ValidationError

        if self.follower == self.following:
            raise ValidationError("自分自身をフォローすることはできません。")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.handle_name} -> {self.following.handle_name}"


class Notification(models.Model):
    """通知モデル"""
    TYPE_CHOICES = [
        ("liked", "liked"),
        ("followed", "followed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications_created"
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor.handle_name} {self.notification_type} to {self.user.handle_name}"


class Report(models.Model):
    """通報モデル"""
    REASON_CHOICES = [
        ("spam", "spam"),
        ("inappropriate", "inappropriate"),
        ("quote", "quote"),
    ]

    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_filed"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("reporter", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report: {self.reason} on {self.post.id}"