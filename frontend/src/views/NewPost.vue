<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";

const router = useRouter();
const text = ref("");
const genre = ref("movie");
const workTitle = ref("");
const performerName = ref("");
const loading = ref(false);
const error = ref("");
const preview = ref("");

const maxTextLength = 136; // 「みたいな」の5文字を考慮

const updatePreview = () => {
  // 末尾に「みたいな」を付与
  if (text.value.endsWith("みたいな")) {
    preview.value = text.value;
  } else {
    preview.value = text.value + "みたいな";
  }
};

const handleTextInput = () => {
  // 136文字を超えたら制限
  if (text.value.length > maxTextLength) {
    text.value = text.value.substring(0, maxTextLength);
  }
  updatePreview();
};

const handleNewPost = async () => {
  if (!text.value.trim()) {
    error.value = "投稿文を入力してください";
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    const response = await api.post("/posts/", {
      text: text.value,
      genre: genre.value,
      work_title: workTitle.value || null,
      performer_name: performerName.value || null,
    });
    router.push(`/p/${response.data.id}`);
  } catch (err) {
    error.value = err.response?.data?.detail || "投稿に失敗しました";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="new-post-container">
    <div class="card mx-auto" style="max-width: 600px">
      <div class="card-body">
        <h3 class="card-title mb-4">新規投稿</h3>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <form @submit.prevent="handleNewPost">
          <div class="mb-3">
            <label for="text" class="form-label">
              投稿文（{{ text.length }}/{{ maxTextLength }}文字）
            </label>
            <textarea
              id="text"
              v-model="text"
              class="form-control"
              rows="4"
              placeholder="みたいなことを思った..."
              @input="handleTextInput"
            ></textarea>
          </div>

          <div class="mb-3">
            <label for="genre" class="form-label">ジャンル</label>
            <select id="genre" v-model="genre" class="form-select">
              <option value="stage">舞台</option>
              <option value="movie">映画</option>
              <option value="novel">小説</option>
              <option value="anime">アニメ</option>
              <option value="manga">マンガ</option>
              <option value="other">その他</option>
            </select>
          </div>

          <div class="mb-3">
            <label for="workTitle" class="form-label">作品名（任意）</label>
            <input
              id="workTitle"
              v-model="workTitle"
              type="text"
              class="form-control"
              placeholder="作品名"
            />
          </div>

          <div class="mb-3">
            <label for="performerName" class="form-label">出演者・作者名（任意）</label>
            <input
              id="performerName"
              v-model="performerName"
              type="text"
              class="form-control"
              placeholder="出演者・作者名"
            />
          </div>

          <!-- プレビュー -->
          <div class="mb-4">
            <label class="form-label">プレビュー</label>
            <div class="card bg-light">
              <div class="card-body">
                <p class="card-text">{{ preview }}</p>
                <small class="text-muted">ジャンル: {{ genre }}</small>
                <div v-if="workTitle" class="mt-2">
                  <small class="text-muted">作品: {{ workTitle }}</small>
                </div>
                <div v-if="performerName" class="mt-1">
                  <small class="text-muted">出演: {{ performerName }}</small>
                </div>
              </div>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            {{ loading ? "投稿中..." : "投稿する" }}
          </button>
        </form>

        <router-link to="/" class="btn btn-outline-secondary w-100 mt-2">
          キャンセル
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.new-post-container {
  max-width: 700px;
  margin: 0 auto;
}
</style>
