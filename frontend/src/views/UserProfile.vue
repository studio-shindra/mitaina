<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../lib/api";
import PostCard from "../components/PostCard.vue";

const route = useRoute();
const router = useRouter();
const user = ref(null);
const posts = ref([]);
const likedPosts = ref([]);
const hatenaPosts = ref([]);
const collectPosts = ref([]);
const loading = ref(true);
const error = ref("");
const isFollowing = ref(false);
const activeTab = ref("posts");

const loadUserData = async () => {
  try {
    const username = route.params.username;
    const response = await api.get(`/users/${username}/`);
    user.value = response.data;
    isFollowing.value = !!response.data.is_followed;
  } catch (err) {
    error.value = "ユーザーが見つかりません";
  }
};

const loadUserPosts = async () => {
  try {
    const username = route.params.username;
    const response = await api.get(`/users/${username}/posts/`);
    posts.value = response.data.results || [];
  } catch (err) {
    error.value = "投稿の読み込みに失敗しました";
    posts.value = [];
  }
};

const loadUserReactions = async (type) => {
  try {
    const username = route.params.username;
    const response = await api.get(`/users/${username}/reactions/?type=${type}`);
    const data = response.data.results || response.data || [];
    
    if (type === "like") {
      likedPosts.value = data;
    } else if (type === "hatena") {
      hatenaPosts.value = data;
    } else if (type === "collect") {
      collectPosts.value = data;
    }
  } catch (err) {
    console.error(`リアクション読み込みエラー (${type}):`, err);
  }
};

const toggleFollow = async () => {
  try {
    const username = route.params.username;
    await api.post(`/users/${username}/follow/`);
    isFollowing.value = !isFollowing.value;
  } catch (err) {
    error.value = "フォロー処理に失敗しました";
  }
};

const handleTabChange = async (tab) => {
  activeTab.value = tab;
  
  // タブ切替時にデータをロード（まだロードしていない場合）
  if (tab === "like" && likedPosts.value.length === 0) {
    await loadUserReactions("like");
  } else if (tab === "hatena" && hatenaPosts.value.length === 0) {
    await loadUserReactions("hatena");
  } else if (tab === "collect" && collectPosts.value.length === 0) {
    await loadUserReactions("collect");
  }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([loadUserData(), loadUserPosts()]);
  loading.value = false;
});
</script>

<template>
  <div class="user-profile-container">
    <div class="user-profile mx-auto" style="max-width: 700px">
      <div class="area">
          <!-- ユーザー情報 -->
          <div v-if="user" class="mb-3">
            <div class="wrap mb-3">
              <div class="fs-5 fw-bold">{{ user.handle_name }}</div>
              <div class="text-muted">@{{ user.username }}</div>
            </div>
            <div class="wrap mb-3">
              <button
                @click="toggleFollow"
                class="btn btn-sm"
                :class="isFollowing ? 'btn-outline-primary' : 'btn-primary'"
              >
                {{ isFollowing ? "フォロー中" : "フォローする" }}
              </button>
            </div>
            <small class="text-muted">
              {{ new Date(user.created_at).toLocaleDateString("ja-JP") }}ぐらいから使ってるみたいです
            </small>
            <div class="small d-flex align-items-center gap-1 mt-2">
              <span class="fw-semibold">{{ user.following_count || 0 }}</span>
              <span class="text-muted">フォロー</span>
              <span class="ms-2 fw-semibold">{{ user.followers_count || 0 }}</span>
              <span class="text-muted">フォロワー</span>
            </div>
          </div>

          <!-- タブナビゲーション -->
          <div class="d-flex align-items-center justify-content-between" role="tablist">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'posts' }"
              @click="activeTab = 'posts'"
              role="tab"
            >
              投稿
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'like' }"
              @click="handleTabChange('like')"
              role="tab"
            >
              いいね
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'hatena' }"
              @click="handleTabChange('hatena')"
              role="tab"
            >
              はてな
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'collect' }"
              @click="handleTabChange('collect')"
              role="tab"
            >
              コレクト
            </button>
          </div>

          <!-- 投稿タブ -->
          <div v-if="activeTab === 'posts'">
            <div v-if="posts.length === 0" class="text-center text-muted py-4">
              投稿がありません
            </div>
            <div v-for="post in posts" :key="post.id">
              <PostCard :post="post" />
            </div>
          </div>

          <!-- いいねタブ -->
          <div v-if="activeTab === 'like'">
            <div v-if="likedPosts.length === 0" class="text-center text-muted py-4">
              いいねがありません
            </div>
            <div v-for="post in likedPosts" :key="post.id">
              <PostCard :post="post" />
            </div>
          </div>

          <!-- はてなタブ -->
          <div v-if="activeTab === 'hatena'">
            <div v-if="hatenaPosts.length === 0" class="text-center text-muted py-4">
              はてながありません
            </div>
            <div v-for="post in hatenaPosts" :key="post.id">
              <PostCard :post="post" />
            </div>
          </div>

          <!-- コレクトタブ -->
          <div v-if="activeTab === 'collect'">
            <div v-if="collectPosts.length === 0" class="text-center text-muted py-4">
              コレクトがありません
            </div>
            <div v-for="post in collectPosts" :key="post.id">
              <PostCard :post="post" />
            </div>
          </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-body {
  cursor: default;
}

.nav-link {
  color: #6c757d;
  border: none;
  cursor: pointer;
  padding: 0.5rem 1rem;
  font-size: 0.95rem;
}

.nav-link:hover {
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.nav-link.active {
  color: #000;
  border-bottom: 2px solid #222222;
  font-weight: 600;
}
</style>
