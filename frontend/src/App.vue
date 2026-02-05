<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const token = ref(localStorage.getItem("token"));

const isLoggedIn = computed(() => !!token.value);

const logout = () => {
  localStorage.removeItem("token");
  token.value = null;
  router.push("/login");
};

// token 変更を監視
const updateToken = (newToken) => {
  token.value = newToken;
};
</script>

<template>
  <div>
    <!-- ナビゲーションバー -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <router-link to="/" class="navbar-brand">MITAINA</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link">Home</router-link>
            </li>
            <template v-if="isLoggedIn">
              <li class="nav-item">
                <router-link to="/new" class="nav-link">新規投稿</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/me" class="nav-link">マイページ</router-link>
              </li>
              <li class="nav-item">
                <a href="#" @click.prevent="logout" class="nav-link">ログアウト</a>
              </li>
            </template>
            <template v-else>
              <li class="nav-item">
                <router-link to="/login" class="nav-link">ログイン</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/register" class="nav-link">登録</router-link>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!-- メインコンテンツ -->
    <main class="container my-4">
      <router-view :key="route.fullPath" @login="(newToken) => { token = newToken; updateToken(newToken); }" />
    </main>
  </div>
</template>

<style scoped>
nav {
  margin-bottom: 1rem;
}
</style>
