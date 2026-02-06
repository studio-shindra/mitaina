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
            <button class="btn btn-sm border-0" @click="$emit('close')">キャンセル</button>
            <button class="btn btn-sm btn-primary rounded-5 px-4" :disabled="loading || text.length === 0" @click="submit">ポストする</button>
          </div>

          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

          <textarea 
          v-model="text" 
          class="form-control" 
          rows="4"
          maxlength="141" 
          placeholder="うろ覚えのセリフ…"
          style="min-height: 30vh;"></textarea>
          <div class="text-secondary small mt-1">{{ remaining }} / 141</div>

          <div class="row mt-3 g-2">
            <div class="col-12">
              <div class="d-flex flex-wrap gap-2">
                <button
                  type="button"
                  class="btn btn-sm rounded-pill"
                  :class="genre === 'stage' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="genre = 'stage'"
                >
                  舞台
                </button>
                <button
                  type="button"
                  class="btn btn-sm rounded-pill"
                  :class="genre === 'movie' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="genre = 'movie'"
                >
                  映画
                </button>
                <button
                  type="button"
                  class="btn btn-sm rounded-pill"
                  :class="genre === 'novel' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="genre = 'novel'"
                >
                  小説
                </button>
                <button
                  type="button"
                  class="btn btn-sm rounded-pill"
                  :class="genre === 'anime' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="genre = 'anime'"
                >
                  アニメ
                </button>
                <button
                  type="button"
                  class="btn btn-sm rounded-pill"
                  :class="genre === 'manga' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="genre = 'manga'"
                >
                  マンガ
                </button>
                <button
                  type="button"
                  class="btn btn-sm rounded-pill"
                  :class="genre === 'other' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="genre = 'other'"
                >
                  その他
                </button>
              </div>
            </div>
            <div class="col-12">
              <input v-model="performer_name" class="form-control" placeholder="演者名（任意）" maxlength="141" />
            </div>
            <div class="col-12">
              <input v-model="work_title" class="form-control" placeholder="作品名（任意）" maxlength="141" />
            </div>
            <div class="col-12">
              <input v-model="character_name" class="form-control" placeholder="役名（任意）" maxlength="141" />
            </div>
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
  align-items: flex-start;
  padding: 16px;
  z-index: 1050;
}
.modal-dialog-custom {
  width: 100%;
  max-width: 560px;
}
</style>
