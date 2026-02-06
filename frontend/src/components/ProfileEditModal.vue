<script setup>
import { ref, watch } from "vue";
import api from "../lib/api";

const props = defineProps({
  show: { type: Boolean, required: true },
  user: { type: Object, default: () => ({}) },
});

const emit = defineEmits(["close", "updated"]);

const handleName = ref("");
const publicId = ref("");
const email = ref("");
const loading = ref(false);
const error = ref("");
const success = ref("");

// user が変わったら初期値を設定
watch(
  () => props.user,
  (newUser) => {
    if (newUser) {
      handleName.value = newUser.handle_name || "";
      publicId.value = newUser.public_id || newUser.username || "";
      email.value = newUser.email || "";
      error.value = "";
      success.value = "";
    }
  },
  { deep: true }
);

const handleSubmit = async () => {
  if (!handleName.value || !publicId.value || !email.value) {
    error.value = "全てのフィールドを入力してください";
    return;
  }

  loading.value = true;
  error.value = "";
  success.value = "";

  try {
    const response = await api.patch("/users/me/", {
      handle_name: handleName.value,
      public_id: publicId.value,
      email: email.value,
    });

    success.value = "プロフィールを更新しました";
    setTimeout(() => {
      emit("updated", response.data);
      emit("close");
    }, 1000);
  } catch (err) {
    error.value =
      err.response?.data?.detail ||
      err.response?.data?.non_field_errors?.[0] ||
      "更新に失敗しました";
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  emit("close");
};
</script>

<template>
  <div v-if="show" class="modal d-block" style="background-color: rgba(0, 0, 0, 0.5)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">プロフィール編集</h5>
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
              <label for="handleName" class="form-label">表示名</label>
              <input
                id="handleName"
                v-model="handleName"
                type="text"
                class="form-control"
                placeholder="例: テストユーザー"
              />
            </div>

            <div class="mb-3">
              <label for="publicId" class="form-label">@ID</label>
              <input
                id="publicId"
                v-model="publicId"
                type="text"
                class="form-control"
                placeholder="例: user123"
              />
              <small class="text-muted">変更するとプロフィール URL も変わります</small>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">メールアドレス</label>
              <input
                id="email"
                v-model="email"
                type="email"
                class="form-control"
                placeholder="例: user@example.com"
              />
            </div>

            <div class="d-grid gap-2">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                {{ loading ? "保存中..." : "保存" }}
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
