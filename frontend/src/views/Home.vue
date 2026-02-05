<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api, { fetchPage } from "../lib/api";

const posts = ref([]);
const loading = ref(false);
const error = ref("");
const search = ref("");
const genre = ref("");
const ordering = ref("-created_at");
const nextUrl = ref(null);
const token = ref(localStorage.getItem("token"));

const isLoggedIn = computed(() => !!token.value);

// 投稿一覧を取得
const fetchPosts = async (url = "/posts/") => {
  loading.value = true;
  error.value = "";
  try {
    const params = {};
    if (search.value) params.search = search.value;
    if (genre.value) params.genre = genre.value;
    if (ordering.value) params.ordering = ordering.value;

    let response;
    if (url === "/posts/") {
      // 初回またはリセット時
      response = await api.get(url, { params });
    } else {
      // ページネーション時（nextUrl は絶対URL の可能性）
      response = await fetchPage(url);
    }
    
    posts.value = response.data.results || response.data;
    nextUrl.value = response.data.next || null;
  } catch (err) {
    error.value = "投稿の読み込みに失敗しました";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// 検索・フィルター・並び替えをリセット
const handleSearch = () => {
  fetchPosts();
};

const handleLoadMore = () => {
  if (nextUrl.value) {
    fetchPosts(nextUrl.value);
  }
};

onMounted(() => {
  fetchPosts();
});

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString("ja-JP");
};

const getGenreLabel = (genre) => {
  const labels = {
    stage: "舞台",
    movie: "映画",
    novel: "小説",
    anime: "アニメ",
    manga: "マンガ",
    other: "その他",
  };
  return labels[genre] || genre;
};
</script>

<template>
  <div class="home">
    <h1 class="mb-4">投稿一覧</h1>

    <!-- エラー表示 -->
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- 検索・フィルター -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <input
            v-model="search"
            type="text"
            class="form-control"
            placeholder="投稿を検索..."
            @keyup.enter="handleSearch"
          />
          <button class="btn btn-primary" @click="handleSearch">検索</button>
        </div>
      </div>
      <div class="col-md-3">
        <select v-model="genre" class="form-select" @change="handleSearch">
          <option value="">全ジャンル</option>
          <option value="stage">舞台</option>
          <option value="movie">映画</option>
          <option value="novel">小説</option>
          <option value="anime">アニメ</option>
          <option value="manga">マンガ</option>
          <option value="other">その他</option>
        </select>
      </div>
      <div class="col-md-3">
        <select v-model="ordering" class="form-select" @change="handleSearch">
          <option value="-created_at">新着順</option>
          <option value="-like_count">いいね順</option>
          <option value="-hatena_count">はてな順</option>
          <option value="-correct_count">正確な引用順</option>
        </select>
      </div>
    </div>

    <!-- ローディング -->
    <div v-if="loading" class="spinner-border" role="status">
      <span class="visually-hidden">読み込み中...</span>
    </div>

    <!-- 投稿一覧 -->
    <div v-else class="row">
      <div v-for="post in posts" :key="post.id" class="col-md-6 mb-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">
              <router-link :to="`/u/${post.author.public_id}`">
                {{ post.author.handle_name }}
              </router-link>
            </h5>
            <p class="card-text">{{ post.text }}</p>
            <small class="text-muted">
              ジャンル: <span class="badge bg-secondary">{{ getGenreLabel(post.genre) }}</span>
            </small>
            <div v-if="post.work_title" class="mt-2">
              <small class="text-muted">作品: {{ post.work_title }}</small>
            </div>
            <div v-if="post.performer_name" class="mt-1">
              <small class="text-muted">出演: {{ post.performer_name }}</small>
            </div>
            <div class="mt-3">
              <small class="text-muted">{{ formatDate(post.created_at) }}</small>
            </div>
            <div class="mt-3">
              <span class="badge bg-info me-2">👍 {{ post.like_count }}</span>
              <span class="badge bg-warning me-2">❓ {{ post.hatena_count }}</span>
              <span class="badge bg-danger me-2">🚫 {{ post.correct_count }}</span>
            </div>
            <router-link :to="`/p/${post.id}`" class="btn btn-sm btn-outline-primary mt-3">
              詳細を見る
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- もっと読む -->
    <div v-if="nextUrl && !loading" class="mt-4 text-center">
      <button class="btn btn-outline-secondary" @click="handleLoadMore">
        もっと読む
      </button>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  transition: box-shadow 0.3s;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-title {
  margin-bottom: 0.5rem;
}

.card-title a {
  text-decoration: none;
  color: #0d6efd;
}

.card-title a:hover {
  text-decoration: underline;
}
</style>
