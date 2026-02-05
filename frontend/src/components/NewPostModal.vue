<script setup>
import { ref, computed, watch } from "vue";
import api from "../lib/api";

const props = defineProps({
  show: { type: Boolean, required: true },
});
const emit = defineEmits(["close", "posted"]);

const text = ref("");
const genre = ref("stage");
const work_title = ref("");
const performer_name = ref("");
const character_name = ref("");
const error = ref("");
const loading = ref(false);

const remaining = computed(() => 141 - text.value.length);
const preview = computed(() => {
  const t = text.value.trimEnd();
  if (!t) return "";
  return t.endsWith("みたいな") ? t : `${t}\nみたいな`;
});

watch(
  () => props.show,
  (v) => {
    if (v) {
      // open時に初期化したければここ
      error.value = "";
    }
  }
);

const submit = async () => {
  error.value = "";
  loading.value = true;
  try {
    await api.post("/posts/", {
      text: text.value,
      genre: genre.value,
      work_title: work_title.value,
      performer_name: performer_name.value,
      character_name: character_name.value,
    });
    emit("posted");
    emit("close");
    // reset
    text.value = "";
    genre.value = "stage";
    work_title.value = "";
    performer_name.value = "";
    character_name.value = "";
  } catch (e) {
    error.value = "投稿に失敗しました";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom">
    <div class="modal-dialog-custom">
      <div class="card">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="fw-semibold">投稿</div>
            <button class="btn btn-sm btn-outline-secondary" @click="$emit('close')">閉じる</button>
          </div>

          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

          <textarea v-model="text" class="form-control" rows="4" maxlength="141" placeholder="うろ覚えのセリフ…"></textarea>
          <div class="text-secondary small mt-1">{{ remaining }} / 141</div>

          <div class="row mt-3 g-2">
            <div class="col-6">
              <select v-model="genre" class="form-select">
                <option value="stage">舞台</option>
                <option value="movie">映画</option>
                <option value="novel">小説</option>
                <option value="anime">アニメ</option>
                <option value="manga">マンガ</option>
                <option value="other">その他</option>
              </select>
            </div>
            <div class="col-6">
              <input v-model="performer_name" class="form-control" placeholder="演者名（任意）" maxlength="141" />
            </div>
            <div class="col-12">
              <input v-model="work_title" class="form-control" placeholder="作品名（任意）" maxlength="141" />
            </div>
            <div class="col-12">
              <input v-model="character_name" class="form-control" placeholder="役名（任意）" maxlength="141" />
            </div>
          </div>

          <div class="mt-3">
            <div class="text-secondary small mb-1">プレビュー</div>
            <div class="border rounded p-2" style="white-space: pre-wrap; min-height: 3em;">
              {{ preview || "（まだない）" }}
            </div>
          </div>

          <div class="d-grid mt-3">
            <button class="btn btn-primary" :disabled="loading || text.length === 0" @click="submit">
              投稿する
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding: 16px;
  z-index: 1050;
}
.modal-dialog-custom {
  width: 100%;
  max-width: 560px;
}
</style>
