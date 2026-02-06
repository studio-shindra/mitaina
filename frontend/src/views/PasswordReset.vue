<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import PasswordResetConfirmModal from "../components/PasswordResetConfirmModal.vue";

const route = useRoute();
const router = useRouter();
const showModal = ref(true);
const modalRef = ref(null);

onMounted(() => {
  // URLパラメータを抽出
  const uid = route.query.uid;
  const token = route.query.token;

  if (uid && token) {
    // モーダルに初期化指示
    if (modalRef.value) {
      modalRef.value.initializeFromUrl(`uid=${uid}&token=${token}`);
    }
  }
});

const handleResetComplete = () => {
  // ログイン画面へリダイレクト
  router.push("/login");
};

const handleModalClose = () => {
  // リセット画面を閉じてホーム画面へ
  router.push("/");
};
</script>

<template>
  <div class="reset-confirmation-container">
    <PasswordResetConfirmModal
      ref="modalRef"
      :show="showModal"
      @close="handleModalClose"
      @reset-complete="handleResetComplete"
    />
  </div>
</template>

<style scoped>
.reset-confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
</style>
