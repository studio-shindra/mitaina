<script setup>
import { ref } from "vue";
import api from "../lib/api";

const props = defineProps({
  show: { type: Boolean, required: true },
});

const emit = defineEmits(["close"]);

const oldPassword = ref("");
const newPassword1 = ref("");
const newPassword2 = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");

const handleSubmit = async () => {
  // バリデーション
  if (!oldPassword.value || !newPassword1.value || !newPassword2.value) {
    error.value = "全てのフィールドを入力してください";
    return;
  }

  if (newPassword1.value !== newPassword2.value) {
    error.value = "新しいパスワードが一致しません";
    return;
  }

  if (newPassword1.value.length < 8) {
    error.value = "パスワードは8文字以上である必要があります";
    return;
  }

  loading.value = true;
  error.value = "";
  success.value = "";

  try {
    await api.post("/auth/password/change/", {
      old_password: oldPassword.value,
      new_password1: newPassword1.value,
      new_password2: newPassword2.value,
    });

    success.value = "パスワードを変更しました";
    setTimeout(() => {
      handleCancel();
    }, 1500);
  } catch (err) {
    error.value =
      err.response?.data?.detail ||
      err.response?.data?.old_password?.[0] ||
      err.response?.data?.non_field_errors?.[0] ||
      "パスワード変更に失敗しました";
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  // フォームリセット
  oldPassword.value = "";
  newPassword1.value = "";
  newPassword2.value = "";
  error.value = "";
  success.value = "";
  emit("close");
};
</script>

<template>
  <div v-if="show" class="modal d-block" style="background-color: rgba(0, 0, 0, 0.5)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">パスワード変更</h5>
          <button
            type="button"
            class="btn-close"
            @click="handleCancel"
          ></button>
        </div>
        <div class="modal-body">
          <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            {{ error }}
            <button
              type="button"
              class="btn-close"
              @click="error = ''"
            ></button>
          </div>

          <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
            {{ success }}
            <button
              type="button"
              class="btn-close"
              @click="success = ''"
            ></button>
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="oldPassword" class="form-label">現在のパスワード</label>
              <input
                id="oldPassword"
                v-model="oldPassword"
                type="password"
                class="form-control"
                placeholder="現在のパスワードを入力"
              />
            </div>

            <div class="mb-3">
              <label for="newPassword1" class="form-label">新しいパスワード</label>
              <input
                id="newPassword1"
                v-model="newPassword1"
                type="password"
                class="form-control"
                placeholder="新しいパスワードを入力"
              />
              <small class="text-muted">8文字以上である必要があります</small>
            </div>

            <div class="mb-3">
              <label for="newPassword2" class="form-label">新しいパスワード（確認）</label>
              <input
                id="newPassword2"
                v-model="newPassword2"
                type="password"
                class="form-control"
                placeholder="新しいパスワードを再入力"
              />
            </div>

            <div class="d-grid gap-2">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                {{ loading ? "変更中..." : "変更" }}
              </button>
              <button
                type="button"
                class="btn btn-secondary"
                @click="handleCancel"
                :disabled="loading"
              >
                キャンセル
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1050;
}

.modal-dialog {
  max-width: 500px;
}
</style>
