<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../lib/api";

const route = useRoute();
const router = useRouter();
const user = ref(null);
const posts = ref([]);
const loading = ref(true);
const error = ref("");
const isFollowing = ref(false);

const loadUserData = async () => {
  try {
    const username = route.params.username;
    const response = await api.get(`/users/${username}/`);
    user.value = response.data;
    isFollowing.value = response.data.is_followed;
  } catch (err) {
    error.value = "ユーザーが見つかりません";
  }
};

const loadUserPosts = async () => {
  try {
    const username = route.params.username;
    // 正規 API エンドポイント：GET /api/users/{username}/posts/
    const response = await api.get(`/users/${username}/posts/`);
    posts.value = response.data.results || [];
  } catch (err) {
    error.value = "投稿の読み込みに失敗しました";
    posts.value = [];
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

const goToPost = (postId) => {
  router.push(`/p/${postId}`);
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([loadUserData(), loadUserPosts()]);
  loading.value = false;
});
</script>

<template>
  <div class="user-profile-container">
    <div class="card mx-auto" style="max-width: 700px">
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <template v-else>
          <!-- ユーザー情報 -->
          <div v-if="user" class="mb-4">
            <h3 class="card-title mb-2">{{ user.username }}</h3>
            <p class="card-text text-muted">@{{ user.handle_name }}</p>
            <small class="text-muted">
              参加日: {{ new Date(user.created_at).toLocaleDateString("ja-JP") }}
            </small>
            <div class="mt-3">
              <button
                @click="toggleFollow"
                class="btn"
                :class="isFollowing ? 'btn-outline-primary' : 'btn-primary'"
              >
                {{ isFollowing ? "フォロー中" : "フォローする" }}
              </button>
            </div>
          </div>

          <hr />

          <!-- ユーザーの投稿 -->
          <h5 class="mb-3">投稿（{{ posts.length }}）</h5>
          <div v-if="posts.length === 0" class="text-center text-muted py-4">
            投稿がありません
          </div>
          <div v-for="post in posts" :key="post.id" class="card mb-3">
            <div class="card-body" @click="goToPost(post.id)" style="cursor: pointer">
              <p class="card-text">{{ post.text }}</p>
              <small class="text-muted">ジャンル: {{ post.genre }}</small>
              <div v-if="post.work_title" class="mt-2">
                <small class="text-muted">作品: {{ post.work_title }}</small>
              </div>
              <div class="mt-2">
                <span class="badge bg-secondary me-2">
                  いいね: {{ post.like_count || 0 }}
                </span>
                <span class="badge bg-secondary me-2">
                  いやちゃう: {{ post.hatena_count || 0 }}
                </span>
                <span class="badge bg-secondary">
                  なるほど: {{ post.correct_count || 0 }}
                </span>
              </div>
            </div>
          </div>

          <router-link to="/" class="btn btn-outline-secondary w-100 mt-3">
            ホームに戻る
          </router-link>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-profile-container {
  max-width: 700px;
  margin: 0 auto;
}

.card-body {
  cursor: default;
}
</style>
