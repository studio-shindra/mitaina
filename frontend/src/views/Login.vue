<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";
import PasswordResetModal from "../components/PasswordResetModal.vue";

const router = useRouter();
const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");
const showPasswordResetModal = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = "ユーザー名とパスワードを入力してください";
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    const response = await api.post("/auth/login/", {
      username: username.value,
      password: password.value,
    });
    const token = response.data.key;
    localStorage.setItem("token", token);
    router.push("/");
  } catch (err) {
    error.value = err.response?.data?.non_field_errors?.[0] || "ログインに失敗しました";
  } finally {
    loading.value = false;
  }
};

const handlePasswordResetOpen = () => {
  showPasswordResetModal.value = true;
};

const handlePasswordResetClose = () => {
  showPasswordResetModal.value = false;
};
</script>

<template>
  <div class="login-container">
    <div class="card mx-auto w-100 border-0" style="max-width: 400px">
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="username" class="form-label">ユーザー名</label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="form-control"
              placeholder="ユーザー名"
            />
          </div>

          <div class="mb-3">
            <label for="password" class="form-label">パスワード</label>
            <input
              id="password"
              v-model="password"
              type="password"
              class="form-control"
              placeholder="パスワード"
            />
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? "ログイン中..." : "ログイン" }}
          </button>
        </form>

        <div class="mt-5 df-center flex-column small">
            <div>アカウントがありませんか？</div>
            <router-link to="/register" class="btn btn-sm btn-link">登録はこちら</router-link>
            <div class="mt-3">パスワードを忘れた場合</div>
            <button
              type="button"
              class="btn btn-sm btn-link"
              @click="handlePasswordResetOpen"
            >
              パスワードリセット
            </button>
        </div>
      </div>
    </div>

    <!-- パスワードリセットモーダル -->
    <PasswordResetModal
      :show="showPasswordResetModal"
      @close="handlePasswordResetClose"
    />
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}
</style>
