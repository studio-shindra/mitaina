from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router でビューセットを登録
router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"posts", views.PostViewSet, basename="post")
router.register(r"feed", views.FeedViewSet, basename="feed")
router.register(r"me/reactions", views.MeReactionsViewSet, basename="me-reactions")
router.register(r"me/notifications", views.MeNotificationsViewSet, basename="me-notifications")

urlpatterns = [
    path("", include(router.urls)),
]