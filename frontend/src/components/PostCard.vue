<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { IconHeart, IconHelpOctagon, IconCircleX, IconPaperclip, IconHeartFilled, IconHelpOctagonFilled, IconCircleXFilled } from '@tabler/icons-vue';
import api from "../lib/api";

const router = useRouter();
const props = defineProps({
  post: { type: Object, required: true },
});

const isLiked = ref(false);
const isHatena = ref(false);
const isCorrect = ref(false);
const isCollect = ref(false);

// ローカルカウント（props を直接編集しない）
const likeCount = ref(props.post.like_count || 0);
const hatenaCount = ref(props.post.hatena_count || 0);
const correctCount = ref(props.post.correct_count || 0);
const collectCount = ref(props.post.collect_count || 0);

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

const getPair = (type) => {
  switch (type) {
    case "like": return { flag: isLiked, count: likeCount };
    case "hatena": return { flag: isHatena, count: hatenaCount };
    case "correct": return { flag: isCorrect, count: correctCount };
    case "collect": return { flag: isCollect, count: collectCount };
    default: return null;
  }
};

const toggleReaction = async (type) => {
  const token = localStorage.getItem("token");
  if (!token) {
    router.push("/login");
    return;
  }

  const pair = getPair(type);
  if (!pair) return;

  const { flag, count } = pair;
  const was = flag.value;
  const old = count.value;

  // optimistic
  flag.value = !was;
  count.value = was ? Math.max(0, old - 1) : old + 1;

  try {
    await api.post(`/posts/${props.post.id}/react/`, { reaction_type: type });
  } catch (e) {
    // rollback
    flag.value = was;
    count.value = old;
  }
};
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
                <div class="text-end text-secondary small fst-italic noto-mincho c-name d-flex align-items-center gap-1">
                    {{ post.character_name || 'あのキャラ' }}
                </div>
            </div>
            <div class="d-flex align-items-center">
                <div class="text-secondary small">{{ post.work_title || 'なんだっけな' }}</div>
                <div>/</div>
                <div class="text-secondary small">{{ post.performer_name || 'あの人' }}</div>
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
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="toggleReaction('like')">
                  <component :is="isLiked ? IconHeartFilled : IconHeart" />
                </button>
                <span>{{ likeCount }}</span>
            </div>
            <div class="d-flex align-items-center gap-1">
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="toggleReaction('hatena')">
                  <component :is="isHatena ? IconHelpOctagonFilled : IconHelpOctagon" />
                </button>
                <span>{{ hatenaCount }}</span>
            </div>
            <div class="d-flex align-items-center gap-1">
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="toggleReaction('correct')">
                  <component :is="isCorrect ? IconCircleXFilled : IconCircleX" />
                </button>
                <span>{{ correctCount }}</span>
            </div>
            <div class="d-flex align-items-center gap-1">
                <button class="btn btn-sm p-0 border-0 bg-transparent" @click="toggleReaction('collect')">
                  <component :is="isCollect ? IconPaperclip : IconPaperclip" :stroke-width="isCollect ? 2.5 : 1.5" />
                </button>
                <span>{{ collectCount }}</span>
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
