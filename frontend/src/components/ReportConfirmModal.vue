<script setup>
import { ref } from "vue";

const props = defineProps({
  show: { type: Boolean, default: false },
});

const emit = defineEmits(["close", "confirm"]);

const handleConfirm = () => {
  emit("confirm");
};

const handleClose = () => {
  emit("close");
};
</script>

<template>
  <div
    v-if="show"
    class="modal fade show d-block"
    tabindex="-1"
    style="background-color: rgba(0, 0, 0, 0.5)"
    @click.self="handleClose"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header border-0">
          <button
            type="button"
            class="btn-close"
            @click="handleClose"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <p class="mb-3">
            あなたの正確な記憶力に敬意を表したい。<br>
            しかしそのセリフが正確であればあるほど我々ミタイナは存続の危機に瀕してしまう。<br>
            言葉を愛してくれてありがとう。しかし今その正しさは著作権のあれこれに巻き込まれる危険な槍となるのだ。
          </p>
          <small class="text-muted">この通報ひとつにつき投稿がちょっとずつ薄くなります。</small>
        </div>
        <div class="modal-footer border-0">
          <button type="button" class="btn btn-secondary" @click="handleClose">
            やめる
          </button>
          <button type="button" class="btn btn-danger" @click="handleConfirm">
            正しさとは時に罪である
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
