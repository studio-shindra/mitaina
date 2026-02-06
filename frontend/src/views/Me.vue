<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { IconDots } from '@tabler/icons-vue';
import api from "../lib/api";
import PostCard from "../components/PostCard.vue";
import ProfileEditModal from "../components/ProfileEditModal.vue";
import PasswordChangeModal from "../components/PasswordChangeModal.vue";

const router = useRouter();
const user = ref(null);
const posts = ref([]);
const likedPosts = ref([]);
const hatenaPosts = ref([]);
const correctPosts = ref([]);
const loading = ref(true);
const error = ref("");
const activeTab = ref("posts");
const showProfileEditModal = ref(false);
const showPasswordChangeModal = ref(false);
const showMenu = ref(false);

const loadUserData = async () => {
  try {
    const response = await api.get("/users/me/");
    user.value = response.data;
  } catch (err) {
    error.value = "ユーザー情報の読み込みに失敗しました";
  }
};

const loadUserPosts = async () => {
  try {
    if (!user.value) return;

    const username = user.value.public_id || user.value.username;
    const response = await api.get(`/users/${username}/posts/`);
    posts.value = response.data.results || [];
  } catch (err) {
    error.value = "投稿の読み込みに失敗しました";
    posts.value = [];
  }
};

const loadUserReactions = async (type) => {
  try {
    const response = await api.get(`/me/reactions/?type=${type}`);
    const data = response.data.results || response.data || [];
    
    if (type === "like") {
      likedPosts.value = data;
    } else if (type === "hatena") {
      hatenaPosts.value = data;
    } else if (type === "correct") {
      correctPosts.value = data;
    }
  } catch (err) {
    console.error(`リアクション読み込みエラー (${type}):`, err);
  }
};

const handleTabChange = async (tab) => {
  activeTab.value = tab;
  
  // タブ切替のたびに必ずAPI再取得
  if (tab === "like") await loadUserReactions("like");
  if (tab === "hatena") await loadUserReactions("hatena");
  if (tab === "correct") await loadUserReactions("correct");
};

const handleLogout = () => {
  localStorage.removeItem("token");
  router.push("/login");
};

const handleProfileEditOpen = () => {
  showProfileEditModal.value = true;
};

const handleProfileEditClose = () => {
  showProfileEditModal.value = false;
};

const handleProfileUpdated = (updatedUser) => {
  user.value = updatedUser;
  // 注: @ID が変わった場合、後で必要に応じて router.replace を呼ぶ
};

const handlePasswordChangeOpen = () => {
  showPasswordChangeModal.value = true;
};

const handlePasswordChangeClose = () => {
  showPasswordChangeModal.value = false;
};

const toggleMenu = () => {
  showMenu.value = !showMenu.value;
};

onMounted(async () => {
  loading.value = true;
  await loadUserData();
  await loadUserPosts();
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
              <div class="text-muted">@{{ user.public_id || user.username }}</div>
            </div>
            <!-- ※プロフィール編集ボタンでできるようにしたい -->
            <div class="change mb-3 d-flex gap-2 align-items-center justify-content-between">
              <button
                class="btn btn-sm btn-primary rounded-5 px-3"
                @click="handleProfileEditOpen"
              >
                プロフィール編集
              </button>
              
              <!-- ドロップダウンメニュー -->
              <div class="dropdown" style="position: relative;">
                <button
                  class="btn btn-sm p-2"
                  @click="toggleMenu"
                  style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;"
                >
                  <IconDots :size="20" />
                </button>
                
                <div
                  v-if="showMenu"
                  class="dropdown-menu show"
                  style="position: absolute; right: 0; top: 100%; margin-top: 4px;"
                  @click="showMenu = false"
                >
                  <button
                    class="dropdown-item"
                    @click="handlePasswordChangeOpen"
                  >
                    パスワード変更
                  </button>
                  <button
                    class="dropdown-item text-danger"
                    @click="handleLogout"
                  >
                    ログアウト
                  </button>
                </div>
              </div>
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
              :class="{ active: activeTab === 'correct' }"
              @click="handleTabChange('correct')"
              role="tab"
            >
              正確な引用
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
          <div v-if="activeTab === 'correct'">
            <div v-if="correctPosts.length === 0" class="text-center text-muted py-4">
              正確な引用がありません
            </div>
            <div v-for="post in correctPosts" :key="post.id">
              <PostCard :post="post" />
            </div>
          </div>

          <!-- ログアウトボタン -->
          <!-- <button
            @click="handleLogout"
            class="btn btn-outline-danger w-100 mt-4"
          >
            ログアウト
          </button> -->
      </div>
    </div>

    <!-- プロフィール編集モーダル -->
    <ProfileEditModal
      :show="showProfileEditModal"
      :user="user"
      @close="handleProfileEditClose"
      @updated="handleProfileUpdated"
    />

    <!-- パスワード変更モーダル -->
    <PasswordChangeModal
      :show="showPasswordChangeModal"
      @close="handlePasswordChangeClose"
    />
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
