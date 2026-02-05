from rest_framework import serializers
from .models import User, Post, Reaction, Follow, Notification, Report


class RegisterSerializer(serializers.ModelSerializer):
    """登録シリアライザー（handle_name を含める）"""
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "handle_name", "email", "password1", "password2")

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "パスワードが一致しません。"})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data, password=password)
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    """ユーザーの公開情報シリアライザー"""
    public_id = serializers.CharField(source="username", read_only=True)

    class Meta:
        model = User
        fields = ("id", "public_id", "handle_name")


class UserDetailSerializer(serializers.ModelSerializer):
    """ユーザーの詳細情報シリアライザー"""
    public_id = serializers.CharField(source="username")

    class Meta:
        model = User
        fields = ("id", "public_id", "handle_name", "email")
        read_only_fields = ("id",)


class PostSerializer(serializers.ModelSerializer):
    """投稿シリアライザー"""
    author = UserPublicSerializer(read_only=True)
    reaction_counts = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "text",
            "genre",
            "work_title",
            "performer_name",
            "like_count",
            "hatena_count",
            "correct_count",
            "reaction_counts",
            "created_at",
        )
        read_only_fields = ("id", "author", "like_count", "hatena_count", "correct_count", "created_at")

    def validate_text(self, value):
        """テキストが141文字以内か検証"""
        # 「みたいな」を付与することを考慮して、141 - 5 = 136 文字で制限
        if len(value) > 136:
            raise serializers.ValidationError("テキストは最大136文字です（「みたいな」を含むため）。")
        return value

    def get_reaction_counts(self, obj):
        """リアクション数を取得"""
        return {
            "like": obj.like_count,
            "hatena": obj.hatena_count,
            "correct": obj.correct_count,
        }


class ReactionToggleSerializer(serializers.Serializer):
    """リアクション切り替えシリアライザー"""
    reaction_type = serializers.ChoiceField(choices=["like", "hatena", "correct"])

    def validate_reaction_type(self, value):
        if value not in ["like", "hatena", "correct"]:
            raise serializers.ValidationError(f"Invalid reaction type: {value}")
        return value


class ReactionSerializer(serializers.ModelSerializer):
    """リアクション詳細シリアライザー"""
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ("id", "user", "post", "reaction_type", "created_at")
        read_only_fields = ("id", "user", "created_at")


class ReportSerializer(serializers.ModelSerializer):
    """通報シリアライザー"""
    reporter = UserPublicSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ("id", "reporter", "post", "reason", "created_at")
        read_only_fields = ("id", "reporter", "post", "created_at")

    def validate_reason(self, value):
        if value not in ["spam", "inappropriate", "quote"]:
            raise serializers.ValidationError(f"Invalid reason: {value}")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """通知シリアライザー"""
    actor = UserPublicSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "actor", "notification_type", "post", "is_read", "created_at")
        read_only_fields = ("id", "actor", "notification_type", "post", "created_at")


class FollowSerializer(serializers.ModelSerializer):
    """フォロー/フォロワーシリアライザー"""
    follower = UserPublicSerializer(read_only=True)
    following = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")
        read_only_fields = ("id", "created_at")
