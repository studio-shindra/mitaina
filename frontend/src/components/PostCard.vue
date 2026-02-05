<script setup>
import { computed, ref } from "vue";
import { IconHeart, IconHelpOctagon, IconCircleX, IconHeartFilled, IconHelpOctagonFilled, IconCircleXFilled } from '@tabler/icons-vue';

const props = defineProps({
  post: { type: Object, required: true },
});

const isLiked = ref(false);
const isHatena = ref(false);
const isCorrect = ref(false);

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("ja-JP");
};

const genreLabel = computed(() => {
  const labels = {
    stage: "舞台",
    movie: "映画",
    novel: "小説",
    anime: "アニメ",
    manga: "マンガ",
    other: "その他",
  };
  return labels[props.post.genre] || props.post.genre;
});
</script>

<template>
  <div class="post h-100 border-bottom py-4">
    <div class="post-body">
      <div class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-2">
            <router-link :to="`/u/${post.author.public_id}`" class="text-decoration-none fw-bold">
                {{ post.author.handle_name }}
            </router-link>
            <span class="text-secondary">@{{ post.author.public_id }}</span>
            <span class="text-secondary small">{{ formatDate(post.created_at) }}</span>
        </div>
      </div>

      <div class="main-text-area p-3">
        <p class="fs-5 noto-mincho" style="white-space: pre-wrap;">{{ post.text }}</p>
      </div>
        <div class="d-flex justify-content-between px-3">
            <div class="d-flex d-flex align-items-center justify-content-end">
                <div v-if="post.character_name"
                class="text-end text-secondary small fst-italic noto-mincho c-name d-flex align-items-center gap-1">
                    {{ post.character_name }}
                </div>
                <div v-else class="text-end text-secondary small fst-italic noto-mincho c-name d-flex align-items-center gap-1">あの人</div>
            </div>
            <div class="d-flex align-items-center">
                <div v-if="post.work_title" class="text-secondary small">{{ post.work_title }}</div>
                <div>/</div>
                <div v-if="post.performer_name" class="text-secondary small">{{ post.performer_name }}</div>
            </div>
        </div>

      <!-- <div class="d-flex align-items-center justify-content-between p-3">
          <div class="d-flex align-items-center">
              <div v-if="post.work_title" class="text-secondary small">{{ post.work_title }}</div>
              <div>/</div>
              <div v-if="post.performer_name" class="text-secondary small">{{ post.performer_name }}</div>
          </div>
      </div> -->

      

          <div class="d-flex align-items-center justify-content-around mt-3">
            <div class="d-flex align-items-center gap-1">
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="isLiked = !isLiked">
                  <component :is="isLiked ? IconHeartFilled : IconHeart" />
                </button>
                <span>{{ post.like_count }}</span>
            </div>
            <div class="d-flex align-items-center gap-1">
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="isHatena = !isHatena">
                  <component :is="isHatena ? IconHelpOctagonFilled : IconHelpOctagon" />
                </button>
                <span>{{ post.hatena_count }}</span>
            </div>
            <div class="d-flex align-items-center gap-1">
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="isCorrect = !isCorrect">
                  <component :is="isCorrect ? IconCircleXFilled : IconCircleX" />
                </button>
                <span>{{ post.correct_count }}</span>
            </div>
            <div>
                <span class="badge bg-light text-dark border">{{ genreLabel }}</span>
            </div>
            <div class="mitaina small">
                みたいな
            </div>
          </div>
          

      <!-- <router-link :to="`/p/${post.id}`" class="btn btn-sm btn-outline-primary mt-3">
        詳細を見る
      </router-link> -->
    </div>

  </div>
</template>
