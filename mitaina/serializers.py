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
    following_count = serializers.IntegerField(read_only=True, default=0)
    followers_count = serializers.IntegerField(read_only=True, default=0)
    is_followed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = ("id", "public_id", "handle_name", "following_count", "followers_count", "is_followed")


class UserDetailSerializer(serializers.ModelSerializer):
    """ユーザーの詳細情報シリアライザー"""
    public_id = serializers.CharField(source="username")
    following_count = serializers.IntegerField(read_only=True, default=0)
    followers_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = ("id", "public_id", "handle_name", "email", "following_count", "followers_count")
        read_only_fields = ("id",)

    def validate_public_id(self, value):
        """public_id（username）のバリデーション"""
        import re
        
        # 形式制約：英小文字/数字/_.、先頭英字、3〜20文字
        if not re.match(r"^[a-z][a-z0-9_.]{2,19}$", value):
            raise serializers.ValidationError(
                "3〜20文字の英小文字で始まり、英小文字・数字・._を含む必要があります。"
            )
        
        # 重複チェック（更新時は自分を除外）
        if self.instance and self.instance.username == value:
            # 自分自身の場合は OK
            return value
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("このユーザーID は既に使用されています。")
        
        return value

    def update(self, instance, validated_data):
        """username の更新を public_id から読み込む"""
        if "username" in validated_data:
            instance.username = validated_data["username"]
            validated_data.pop("username")
        return super().update(instance, validated_data)


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
            "character_name",
            "like_count",
            "hatena_count",
            "correct_count",
            "reaction_counts",
            "created_at",
        )
        read_only_fields = ("id", "author", "like_count", "hatena_count", "correct_count", "created_at")

    def validate_text(self, value):
        """テキストが141文字以内か検証"""
        if not value or not value.strip():
            raise serializers.ValidationError("text is required")
        if len(value) > 141:
            raise serializers.ValidationError("text must be <= 141 chars")
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
