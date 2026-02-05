<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";

const router = useRouter();
const user = ref(null);
const reactions = ref({ like: [], hatena: [] });
const notifications = ref([]);
const loading = ref(true);
const error = ref("");
const activeTab = ref("like");

const loadUserData = async () => {
  try {
    const response = await api.get("/users/me/");
    user.value = response.data;
  } catch (err) {
    error.value = "ユーザー情報の読み込みに失敗しました";
  }
};

const loadReactions = async () => {
  try {
    const likeResponse = await api.get("/me/reactions/?reaction_type=like");
    const hatenaResponse = await api.get("/me/reactions/?reaction_type=hatena");
    reactions.value.like = likeResponse.data.results || [];
    reactions.value.hatena = hatenaResponse.data.results || [];
  } catch (err) {
    error.value = "反応の読み込みに失敗しました";
  }
};

const loadNotifications = async () => {
  try {
    const response = await api.get("/me/notifications/");
    notifications.value = response.data.results || [];
  } catch (err) {
    // Notifications が実装されていない場合は無視
    notifications.value = [];
  }
};

const handleLogout = () => {
  localStorage.removeItem("token");
  router.push("/login");
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([loadUserData(), loadReactions(), loadNotifications()]);
  loading.value = false;
});
</script>

<template>
  <div class="me-container">
    <div class="card mx-auto" style="max-width: 700px">
      <div class="card-body">
        <h3 class="card-title mb-4">マイページ</h3>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <template v-else>
          <!-- ユーザー情報 -->
          <div v-if="user" class="card mb-4 bg-light">
            <div class="card-body">
              <h5 class="card-title">{{ user.username }}</h5>
              <p class="card-text text-muted">@{{ user.handle_name }}</p>
              <p class="card-text" v-if="user.email">{{ user.email }}</p>
              <small class="text-muted">
                参加日: {{ new Date(user.created_at).toLocaleDateString("ja-JP") }}
              </small>
            </div>
          </div>

          <!-- タブ切り替え -->
          <ul class="nav nav-tabs mb-3" role="tablist">
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'like' }"
                @click="activeTab = 'like'"
              >
                いいね（{{ reactions.like.length }}）
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'hatena' }"
                @click="activeTab = 'hatena'"
              >
                いやちゃうやろw（{{ reactions.hatena.length }}）
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'notifications' }"
                @click="activeTab = 'notifications'"
              >
                通知
              </button>
            </li>
          </ul>

          <!-- 反応のいいねタブ -->
          <div v-if="activeTab === 'like'">
            <div v-if="reactions.like.length === 0" class="text-center text-muted py-4">
              いいねした投稿がありません
            </div>
            <div v-for="reaction in reactions.like" :key="reaction.id" class="card mb-3">
              <div class="card-body">
                <p class="card-text">{{ reaction.post.text }}</p>
                <small class="text-muted">
                  投稿者: {{ reaction.post.author.username }}
                </small>
              </div>
            </div>
          </div>

          <!-- 反応の「いやちゃうやろw」タブ -->
          <div v-if="activeTab === 'hatena'">
            <div v-if="reactions.hatena.length === 0" class="text-center text-muted py-4">
              「いやちゃうやろw」した投稿がありません
            </div>
            <div v-for="reaction in reactions.hatena" :key="reaction.id" class="card mb-3">
              <div class="card-body">
                <p class="card-text">{{ reaction.post.text }}</p>
                <small class="text-muted">
                  投稿者: {{ reaction.post.author.username }}
                </small>
              </div>
            </div>
          </div>

          <!-- 通知タブ -->
          <div v-if="activeTab === 'notifications'">
            <div v-if="notifications.length === 0" class="text-center text-muted py-4">
              通知がありません
            </div>
            <div v-for="notification in notifications" :key="notification.id" class="card mb-3">
              <div class="card-body">
                <p class="card-text">{{ notification.message }}</p>
                <small class="text-muted">
                  {{ new Date(notification.created_at).toLocaleString("ja-JP") }}
                </small>
              </div>
            </div>
          </div>

          <!-- ログアウトボタン -->
          <button
            @click="handleLogout"
            class="btn btn-outline-danger w-100 mt-4"
          >
            ログアウト
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.me-container {
  max-width: 700px;
  margin: 0 auto;
}

.nav-link {
  color: #6c757d;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  padding: 0.5rem 1rem;
}

.nav-link.active {
  color: #495057;
  border-bottom-color: #007bff;
  font-weight: 600;
}
</style>
