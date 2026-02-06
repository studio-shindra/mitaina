"""API ビュー"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Exists, OuterRef
from django.shortcuts import get_object_or_404

from .models import User, Post, Reaction, Follow, Notification, Report
from .serializers import (
    UserPublicSerializer,
    UserDetailSerializer,
    PostSerializer,
    ReactionToggleSerializer,
    ReactionSerializer,
    ReportSerializer,
    NotificationSerializer,
    FollowSerializer,
)
from .services import toggle_reaction, toggle_follow


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ユーザービューセット（読み取り専用）"""
    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "username"

    def get_queryset(self):
        """フォロー/フォロワー数とis_followedを含むクエリセット"""
        qs = User.objects.all()
        
        # フォロー数とフォロワー数をannotate
        qs = qs.annotate(
            following_count=Count("following_list", distinct=True),
            followers_count=Count("followers_list", distinct=True),
        )
        
        # ログイン中ならis_followedも追加
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_followed=Exists(
                    Follow.objects.filter(
                        follower=self.request.user,
                        following=OuterRef("pk")
                    )
                )
            )
        else:
            # 未ログインの場合はFalseで統一
            qs = qs.annotate(is_followed=Count("id", filter=Q(id__isnull=True)))
        
        return qs

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """自分の情報を取得/更新"""
        # get_querysetを使ってannotateされたユーザーを取得
        queryset = self.get_queryset()
        user = queryset.get(pk=request.user.pk)
        
        if request.method == "GET":
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        
        elif request.method == "PATCH":
            serializer = UserDetailSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # 保存後、再度annotateされたデータを取得
                updated_user = queryset.get(pk=user.pk)
                response_serializer = UserDetailSerializer(updated_user)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def follow(self, request, username=None):
        """ユーザーをフォロー/アンフォロー（トグル）"""
        following = self.get_object()
        follower = request.user
        
        if following == follower:
            return Response(
                {"detail": "自分自身をフォローすることはできません。"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            result = toggle_follow(follower, following)
            return Response(
                {
                    "detail": "フォローしました" if result["created"] else "アンフォローしました",
                    "is_following": result["created"],
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def followers(self, request, username=None):
        """フォロワー一覧"""
        user = self.get_object()
        followers = Follow.objects.filter(following=user).select_related("follower")
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def following(self, request, username=None):
        """フォロー中のユーザー一覧"""
        user = self.get_object()
        following = Follow.objects.filter(follower=user).select_related("following")
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def posts(self, request, username=None):
        """ユーザーの投稿一覧"""
        user = self.get_object()
        posts = Post.objects.filter(author=user, deleted_at__isnull=True).order_by("-created_at")
        
        # ページネーション適用
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def reactions(self, request, username=None):
        """ユーザーのリアクション一覧（タイプ別）"""
        user = self.get_object()
        reaction_type = request.query_params.get("type")
        
        # reaction_type が指定されていない、または無効な場合
        if not reaction_type:
            return Response(
                {"detail": "type parameter is required (like, hatena, correct, collect)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        valid_types = ["like", "hatena", "correct", "collect"]
        if reaction_type not in valid_types:
            return Response(
                {"detail": f"Invalid type. Choose from: {', '.join(valid_types)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Reaction を基準にフィルタ（論理削除を除外）
        reactions = Reaction.objects.filter(
            user=user,
            reaction_type=reaction_type,
            post__deleted_at__isnull=True  # 論理削除を除外
        ).order_by("-created_at").select_related("post", "post__author")
        
        # ページネーション（Reaction を基準）
        page = self.paginate_queryset(reactions)
        if page is not None:
            # リアクションのページから投稿を抽出
            posts = [r.post for r in page]
            serializer = PostSerializer(posts, many=True)
            return self.get_paginated_response(serializer.data)
        
        # ページングなしの場合
        posts = [r.post for r in reactions]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """投稿ビューセット"""
    queryset = Post.objects.filter(deleted_at__isnull=True)
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["genre"]
    search_fields = ["text", "work_title", "performer_name"]
    ordering_fields = ["created_at", "like_count", "hatena_count", "correct_count"]
    ordering = ["-created_at"]

    def get_permissions(self):
        """アクションごとに権限を設定"""
        if self.action in ["create", "destroy", "react", "report"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_throttles(self):
        """アクションごとに throttle scope を設定"""
        if self.action == "create":
            self.throttle_scope = "post_create"
        elif self.action == "react":
            self.throttle_scope = "reaction"
        elif self.action == "report":
            self.throttle_scope = "report"
        return super().get_throttles()

    def perform_create(self, serializer):
        """投稿作成時に著者を設定"""
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """投稿削除時に論理削除"""
        from django.utils import timezone
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def react(self, request, pk=None):
        """リアクションのトグル"""
        post = self.get_object()
        serializer = ReactionToggleSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        reaction_type = serializer.validated_data["reaction_type"]
        
        try:
            result = toggle_reaction(request.user, post, reaction_type)
            return Response(
                {
                    "detail": f"{reaction_type}リアクションを追加しました" if result["created"] else f"{reaction_type}リアクションを削除しました",
                    "is_reacted": result["created"],
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        """投稿を通報"""
        post = self.get_object()
        
        if not request.data.get("reason"):
            return Response(
                {"detail": "reasonは必須です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        reason = request.data.get("reason")
        if reason not in ["spam", "inappropriate", "quote"]:
            return Response(
                {"detail": f"Invalid reason: {reason}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            report, created = Report.objects.get_or_create(
                reporter=request.user,
                post=post,
                defaults={"reason": reason}
            )
            
            if not created:
                return Response(
                    {"detail": "既にこの投稿を通報しています。"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            return Response(
                {"detail": "通報しました。"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeedViewSet(viewsets.ReadOnlyModelViewSet):
    """フィード ビューセット（フォロー中のユーザーの投稿）"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        """フォロー中のユーザーの投稿を取得"""
        user = self.request.user
        following_users = Follow.objects.filter(follower=user).values_list("following", flat=True)
        return Post.objects.filter(
            author_id__in=following_users,
            deleted_at__isnull=True
        ).select_related("author")


class MeReactionsViewSet(viewsets.ViewSet):
    """自分のリアクション ビューセット"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """自分がリアクションした投稿一覧（タイプ別）"""
        reaction_type = request.query_params.get("type")
        
        # reaction_type が指定されていない場合
        if not reaction_type:
            return Response(
                {"detail": "type parameter is required (like, hatena, correct, collect)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        valid_types = ["like", "hatena", "correct", "collect"]
        if reaction_type not in valid_types:
            return Response(
                {"detail": f"Invalid type. Choose from: {', '.join(valid_types)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Reaction を基準にフィルタ（論理削除を除外）
        reactions = Reaction.objects.filter(
            user=request.user,
            reaction_type=reaction_type,
            post__deleted_at__isnull=True
        ).order_by("-created_at").select_related("post", "post__author")
        
        # ページネーション（Reaction を基準）
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(reactions, request)
        if page is not None:
            # リアクションのページから投稿を抽出
            posts = [r.post for r in page]
            serializer = PostSerializer(posts, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # ページングなしの場合
        posts = [r.post for r in reactions]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class MeNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    """自分の通知 ビューセット"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """自分への通知を取得"""
        return Notification.objects.filter(user=self.request.user).select_related("actor", "post")

    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, pk=None):
        """通知を既読にマーク"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def mark_all_as_read(self, request):
        """すべての通知を既読にマーク"""
        self.get_queryset().update(is_read=True)
        return Response({"detail": "すべての通知を既読にしました。"})


# パスワードリセット用リダイレクトビュー（A案）
def password_reset_redirect(request, uidb64, token):
    """
    バックエンドの /accounts/reset/<uid>/<token>/ へのアクセスを
    フロントエンドの /password-reset?uid=...&token=... にリダイレクトする
    """
    from django.shortcuts import redirect
    from django.conf import settings
    
    frontend_url = f"{settings.FRONTEND_BASE_URL}/password-reset?uid={uidb64}&token={token}"
    return redirect(frontend_url)
