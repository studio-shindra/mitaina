<script setup>
import { ref } from "vue";
import api from "../lib/api";

defineProps({
  show: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "reset-complete"]);

const uid = ref("");
const token = ref("");
const newPassword1 = ref("");
const newPassword2 = ref("");
const loading = ref(false);
const message = ref("");
const messageType = ref(""); // success, error
const showPasswordForm = ref(false);

const handleConfirm = async () => {
  if (!uid.value || !token.value) {
    message.value = "リセットトークンが無効です。メールのリンクから再度アクセスしてください。";
    messageType.value = "error";
    return;
  }

  if (!newPassword1.value || !newPassword2.value) {
    message.value = "パスワードを入力してください";
    messageType.value = "error";
    return;
  }

  if (newPassword1.value.length < 8) {
    message.value = "パスワードは8文字以上である必要があります";
    messageType.value = "error";
    return;
  }

  if (newPassword1.value !== newPassword2.value) {
    message.value = "パスワードが一致しません";
    messageType.value = "error";
    return;
  }

  loading.value = true;
  try {
    await api.post("/auth/password/reset/confirm/", {
      uid: uid.value,
      token: token.value,
      new_password1: newPassword1.value,
      new_password2: newPassword2.value,
    });
    message.value = "パスワードをリセットしました。ログインしてください。";
    messageType.value = "success";
    setTimeout(() => {
      emit("reset-complete");
      handleCancel();
    }, 2000);
  } catch (err) {
    message.value =
      err.response?.data?.detail ||
      err.response?.data?.token?.[0] ||
      "リセットに失敗しました。もう一度パスワードリセットから始めてください。";
    messageType.value = "error";
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  uid.value = "";
  token.value = "";
  newPassword1.value = "";
  newPassword2.value = "";
  message.value = "";
  messageType.value = "";
  showPasswordForm.value = false;
  emit("close");
};

// URLパラメータからuidとtokenを取得するメソッド
const initializeFromUrl = (urlParams) => {
  const params = new URLSearchParams(urlParams);
  uid.value = params.get("uid") || "";
  token.value = params.get("token") || "";
  if (uid.value && token.value) {
    showPasswordForm.value = true;
  }
};

defineExpose({
  initializeFromUrl,
});
</script>

<template>
  <div
    v-if="show"
    class="modal d-block"
    tabindex="-1"
    role="dialog"
    style="background-color: rgba(0, 0, 0, 0.5)"
  >
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">パスワードリセット</h5>
          <button
            type="button"
            class="btn-close"
            @click="handleCancel"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <div v-if="!showPasswordForm" class="text-center">
            <p class="text-muted">メールに記載されたリンクからアクセスしてください</p>
          </div>
          <div v-if="showPasswordForm">
            <p class="text-muted small">
              新しいパスワードを入力してください。
            </p>
            <div class="mb-3">
              <label for="new-password1" class="form-label">新しいパスワード</label>
              <input
                id="new-password1"
                v-model="newPassword1"
                type="password"
                class="form-control"
                placeholder="8文字以上"
                :disabled="loading"
              />
            </div>
            <div class="mb-3">
              <label for="new-password2" class="form-label">パスワード確認</label>
              <input
                id="new-password2"
                v-model="newPassword2"
                type="password"
                class="form-control"
                placeholder="もう一度入力"
                :disabled="loading"
              />
            </div>
            <div v-if="message" :class="{ alert: true, 'alert-success': messageType === 'success', 'alert-danger': messageType === 'error' }">
              {{ message }}
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            @click="handleCancel"
            :disabled="loading"
          >
            キャンセル
          </button>
          <button
            v-if="showPasswordForm"
            type="button"
            class="btn btn-primary"
            @click="handleConfirm"
            :disabled="loading || !newPassword1 || !newPassword2"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? "処理中..." : "パスワードリセット" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  display: block;
}
</style>
