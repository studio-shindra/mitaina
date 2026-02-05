import django
import os
import sys

# Django 環境を初期化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/Users/koyanagikokoro/Dropbox/PRODUCTS/MITAINA')
django.setup()

from mitaina.models import User, Post

# テストユーザーを作成
user, user_created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'handle_name': 'テストユーザー',
        'email': 'test@example.com',
    }
)

if user_created:
    user.set_password('testpass123')
    user.save()
    print(f"✅ ユーザー作成: {user.username}")
else:
    print(f"✅ ユーザー取得: {user.username}")

# テスト投稿を作成
posts_data = [
    {
        'text': '映画「インセプション」は本当に面白かった',
        'genre': 'movie',
        'work_title': 'インセプション',
        'performer_name': 'クリストファー・ノーラン',
    },
    {
        'text': '舞台「ハムレット」の演技が素晴らしい',
        'genre': 'stage',
        'work_title': 'ハムレット',
        'performer_name': '竹中直人',
    },
    {
        'text': 'マンガ「進撃の巨人」の世界観が素晴らしい',
        'genre': 'manga',
        'work_title': '進撃の巨人',
        'performer_name': '諫山創',
    },
]

created_count = 0
for data in posts_data:
    post, created = Post.objects.get_or_create(
        author=user,
        text=data['text'],
        defaults={
            'genre': data['genre'],
            'work_title': data.get('work_title'),
            'performer_name': data.get('performer_name'),
        }
    )
    if created:
        created_count += 1
        print(f"✅ 投稿作成: {data['work_title']}")

print(f"\n✅ 新規投稿: {created_count} 件")
total = Post.objects.filter(deleted_at__isnull=True).count()
print(f"✅ 合計投稿数: {total} 件")
