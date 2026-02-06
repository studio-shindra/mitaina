<script setup>
import { ref } from "vue";
import api from "../lib/api";

defineProps({
  show: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "reset-sent"]);

const email = ref("");
const loading = ref(false);
const message = ref("");
const messageType = ref(""); // success, error
const step = ref("email"); // email, confirm

const handleSubmit = async () => {
  if (!email.value) {
    message.value = "メールアドレスを入力してください";
    messageType.value = "error";
    return;
  }

  loading.value = true;
  try {
    await api.post("/auth/password/reset/", {
      email: email.value,
    });
    message.value = "リセットメールを送信しました。メールボックスを確認してください。";
    messageType.value = "success";
    setTimeout(() => {
      emit("reset-sent");
      handleCancel();
    }, 2000);
  } catch (err) {
    message.value =
      err.response?.data?.email?.[0] ||
      "メール送信に失敗しました。メールアドレスをご確認ください。";
    messageType.value = "error";
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  email.value = "";
  message.value = "";
  messageType.value = "";
  step.value = "email";
  emit("close");
};
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
          <div v-if="step === 'email'">
            <p class="text-muted small">
              登録済みのメールアドレスを入力してください。パスワードリセット用のリンクをお送りします。
            </p>
            <div class="mb-3">
              <label for="reset-email" class="form-label">メールアドレス</label>
              <input
                id="reset-email"
                v-model="email"
                type="email"
                class="form-control"
                placeholder="example@domain.com"
                :disabled="loading"
                @keyup.enter="handleSubmit"
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
            type="button"
            class="btn btn-primary"
            @click="handleSubmit"
            :disabled="loading || !email"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? "送信中..." : "リセットメール送信" }}
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
