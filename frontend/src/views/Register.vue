<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";

const router = useRouter();
const username = ref("");
const handleName = ref("");
const email = ref("");
const password1 = ref("");
const password2 = ref("");
const loading = ref(false);
const error = ref("");

const handleRegister = async () => {
  if (!username.value || !handleName.value || !email.value || !password1.value || !password2.value) {
    error.value = "すべてのフィールドを入力してください";
    return;
  }

  if (password1.value !== password2.value) {
    error.value = "パスワードが一致しません";
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    await api.post("/auth/registration/", {
      username: username.value,
      password1: password1.value,
      password2: password2.value,
      email: email.value,
    });
    // 別途 handle_name を更新（ユーザー情報編集）
    // 今はスキップして、ログイン画面へ
    router.push("/login");
  } catch (err) {
    const errors = err.response?.data || {};
    error.value = Object.values(errors).flat().join(" ");
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="register-container">
    <div class="card mx-auto border-0 w-100" style="max-width: 400px">
      <div class="card-body">
        <h3 class="card-title text-center mb-4">新規登録</h3>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label for="username" class="form-label small">ユーザー名（@なし）</label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="form-control"
              placeholder="testuser"
            />
          </div>

          <div class="mb-3">
            <label for="handleName" class="form-label small">表示名</label>
            <input
              id="handleName"
              v-model="handleName"
              type="text"
              class="form-control"
              placeholder="テストのほらあれ"
            />
          </div>

          <div class="mb-3">
            <label for="email" class="form-label small">メールアドレス</label>
            <input
              id="email"
              v-model="email"
              type="email"
              class="form-control"
              placeholder="nandakke@example.com"
            />
          </div>

          <div class="mb-3">
            <label for="password1" class="form-label small">パスワード</label>
            <input
              id="password1"
              v-model="password1"
              type="password"
              class="form-control"
              placeholder="パスワード"
            />
          </div>

          <div class="mb-3">
            <label for="password2" class="form-label small">パスワード（確認）</label>
            <input
              id="password2"
              v-model="password2"
              type="password"
              class="form-control"
              placeholder="パスワード（確認）"
            />
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? "登録中..." : "登録する" }}
          </button>
        </form>

        <div class="mt-5 df-center flex-column small">
            <div>アカウントがありますか？</div>
            <router-link to="/login" class="btn btn-sm btn-link">ログインはこちら</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}
</style>
