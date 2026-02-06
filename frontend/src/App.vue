<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { IconHomeFilled, IconUserFilled } from '@tabler/icons-vue';

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
    <header>
      <div class="wrap py-3 border-bottom w-100 df-center">
        <router-link to="/" class="d-flex align-items-center gap-2 text-decoration-none">
          <img src="../public/icon.svg" style="height: 24px;" alt="">
        </router-link>
      </div>
      
    </header>
    <!-- メインコンテンツ -->
    <main class="container mt-2 mb-5 py-2"
    style="max-width: 768px;">
      <router-view :key="route.fullPath" @login="(newToken) => { token = newToken; updateToken(newToken); }" />
    </main>

    <footer class="position-fixed bottom-0 start-0 w-100 bg-white border-top">
        <nav>
            <ul class="d-flex align-items-center justify-content-around py-3">
                <li>
                  <router-link to="/"><IconHomeFilled :size="24"/></router-link></li>
                <li>
                  <router-link to="/me"><IconUserFilled :size="24"/></router-link></li>
            </ul>
        </nav>
    </footer>
  </div>
</template>
