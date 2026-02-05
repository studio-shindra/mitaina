"""ビジネスロジックサービス"""
from django.db import transaction
from .models import Reaction, Notification, Follow, Post


def toggle_reaction(user, post, reaction_type):
    """
    リアクション のトグル（追加/削除）
    
    Args:
        user: リアクションを行うユーザー
        post: リアクション対象の投稿
        reaction_type: リアクションタイプ ('like', 'hatena', 'correct')
    
    Returns:
        dict: {'created': bool, 'reaction': Reaction or None}
    """
    if reaction_type not in ["like", "hatena", "correct"]:
        raise ValueError(f"Invalid reaction type: {reaction_type}")
    
    try:
        reaction = Reaction.objects.get(user=user, post=post, reaction_type=reaction_type)
        # 既に存在する場合は削除
        reaction.delete()
        
        # カウンタをデクリメント
        if reaction_type == "like":
            post.like_count = max(0, post.like_count - 1)
        elif reaction_type == "hatena":
            post.hatena_count = max(0, post.hatena_count - 1)
        elif reaction_type == "correct":
            post.correct_count = max(0, post.correct_count - 1)
        post.save(update_fields=[f"{reaction_type}_count"])
        
        return {"created": False, "reaction": None}
    
    except Reaction.DoesNotExist:
        # 存在しない場合は新規作成
        reaction = Reaction.objects.create(
            user=user,
            post=post,
            reaction_type=reaction_type
        )
        
        # カウンタをインクリメント
        if reaction_type == "like":
            post.like_count += 1
        elif reaction_type == "hatena":
            post.hatena_count += 1
        elif reaction_type == "correct":
            post.correct_count += 1
        post.save(update_fields=[f"{reaction_type}_count"])
        
        # like のみ通知を作成
        if reaction_type == "like" and user != post.author:
            Notification.objects.get_or_create(
                user=post.author,
                actor=user,
                notification_type="liked",
                post=post,
            )
        
        return {"created": True, "reaction": reaction}


def toggle_follow(follower, following):
    """
    フォロー のトグル（追加/削除）
    
    Args:
        follower: フォロー する側のユーザー
        following: フォロー される側のユーザー
    
    Returns:
        dict: {'created': bool, 'follow': Follow or None}
    """
    if follower == following:
        raise ValueError("自分自身をフォローすることはできません。")
    
    try:
        follow = Follow.objects.get(follower=follower, following=following)
        # 既に存在する場合は削除
        follow.delete()
        return {"created": False, "follow": None}
    
    except Follow.DoesNotExist:
        # 存在しない場合は新規作成
        follow = Follow.objects.create(follower=follower, following=following)
        
        # followed 通知を作成
        Notification.objects.get_or_create(
            user=following,
            actor=follower,
            notification_type="followed",
        )
        
        return {"created": True, "follow": follow}
