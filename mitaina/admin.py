from django.contrib import admin
from .models import User, Post, Reaction, Follow, Notification, Report


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "handle_name", "email", "date_joined")
    search_fields = ("username", "handle_name", "email")
    list_filter = ("date_joined",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "text", "genre", "like_count", "hatena_count", "correct_count", "created_at", "deleted_at")
    search_fields = ("text", "author__handle_name", "work_title", "performer_name")
    list_filter = ("genre", "created_at", "deleted_at")
    readonly_fields = ("created_at",)


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "reaction_type", "created_at")
    search_fields = ("user__handle_name", "post__text")
    list_filter = ("reaction_type", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__handle_name", "following__handle_name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "actor", "notification_type", "is_read", "created_at")
    search_fields = ("user__handle_name", "actor__handle_name")
    list_filter = ("notification_type", "is_read", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "post", "reason", "created_at")
    search_fields = ("reporter__handle_name", "post__text")
    list_filter = ("reason", "created_at")
    readonly_fields = ("created_at",)
