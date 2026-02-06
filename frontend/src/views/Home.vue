<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api, { fetchPage } from "../lib/api";
import PostCard from "../components/PostCard.vue";
import NewPostModal from "../components/NewPostModal.vue";
import { IconCirclePlusFilled, IconSearch, IconUser, IconHome, IconSortDescending } from '@tabler/icons-vue';

const router = useRouter();
const posts = ref([]);
const loading = ref(false);
const error = ref("");
const search = ref("");
const genre = ref("");
const ordering = ref("-created_at");
const nextUrl = ref(null);
const token = ref(localStorage.getItem("token"));
const showNewModal = ref(false);
const showSortMenu = ref(false);
const showSearchInput = ref(false);

const isLoggedIn = computed(() => !!token.value);

const genreTabs = [
  { label: "すべて", value: "" },
  { label: "舞台", value: "stage" },
  { label: "映画", value: "movie" },
  { label: "小説", value: "novel" },
  { label: "アニメ", value: "anime" },
  { label: "マンガ", value: "manga" },
  { label: "その他", value: "other" },
];

const orderingOptions = [
  { label: "新着順", value: "-created_at" },
  { label: "いいね順", value: "-like_count" },
  { label: "はてな順", value: "-hatena_count" },
  { label: "正確な引用順", value: "-correct_count" },
];

// 投稿一覧を取得
const fetchPosts = async ({ reset = false, url = "/posts/" } = {}) => {
  loading.value = true;
  error.value = "";

  try {
    const params = {};
    if (search.value) params.search = search.value;
    if (genre.value) params.genre = genre.value;
    if (ordering.value) params.ordering = ordering.value;

    let response;
    if (url === "/posts/") {
      response = await api.get(url, { params });
    } else {
      response = await fetchPage(url);
    }

    const results = response.data.results || response.data;

    if (reset) {
      posts.value = results;
    } else {
      // もっと読む用：append
      posts.value = posts.value.concat(results);
    }

    nextUrl.value = response.data.next || null;
  } catch (err) {
    error.value = "投稿の読み込みに失敗しました";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// 検索・フィルター・並び替えをリセット
const handleSearch = () => {
  // 条件変えたら必ずリセット
  nextUrl.value = null;
  fetchPosts({ reset: true, url: "/posts/" });
};

const setGenre = (value) => {
  if (genre.value === value) return;
  genre.value = value;
  handleSearch();
};

const setOrdering = (value) => {
  if (ordering.value === value) return;
  ordering.value = value;
  showSortMenu.value = false;
  handleSearch();
};

const handleLoadMore = () => {
  if (nextUrl.value) {
    fetchPosts({ reset: false, url: nextUrl.value });
  }
};

const openNew = () => {
  if (!localStorage.getItem("token")) {
    router.push("/login");
    return;
  }
  showNewModal.value = true;
};

const onPosted = () => {
  // 投稿されたら一覧をリセット再取得
  nextUrl.value = null;
  fetchPosts({ reset: true, url: "/posts/" });
};

onMounted(() => {
  fetchPosts({ reset: true, url: "/posts/" });
});

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString("ja-JP");
};

const getGenreLabel = (genre) => {
  const labels = {
    stage: "舞台",
    movie: "映画",
    novel: "小説",
    anime: "アニメ",
    manga: "マンガ",
    other: "その他",
  };
  return labels[genre] || genre;
};
</script>

<template>
  <div class="home position-relative pb-5">
    <!-- <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="mb-0">投稿一覧</h1>
      <button class="btn btn-primary" @click="openNew">投稿</button>
    </div> -->

    <!-- エラー表示 -->
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- 検索・フィルター -->
    <div class="header d-flex align-items-center justify-content-between gap-3 position-relative">
      <div class="d-flex flex-nowrap gap-3 pb-2 overflow-x-auto flex-grow-1 tab-scroll">
        <button
          v-for="tab in genreTabs"
          :key="tab.value || 'all'"
          class="tab-btn"
          :class="{ active: genre === tab.value }"
          @click="setGenre(tab.value)"
          style="white-space: nowrap;"
        >
          {{ tab.label }}
        </button>
      </div>
      <div class="flex-shrink-0">
        <button class="sort-btn me-2" @click="showSortMenu = !showSortMenu">
          <IconSortDescending />
        </button>
        <div v-if="showSortMenu" class="sort-menu">
          <button
            v-for="opt in orderingOptions"
            :key="opt.value"
            class="sort-item"
            :class="{ active: ordering === opt.value }"
            @click="setOrdering(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
        <button class="search-toggle-btn" @click="showSearchInput = !showSearchInput">
          <IconSearch class="text-dark" />
        </button>
        <div class="search-accordion" :class="{ active: showSearchInput }">
          <input
            v-model="search"
            type="text"
            class="form-control search-input"
            placeholder="投稿を検索..."
            @keyup.enter="handleSearch"
          />
          <button class="btn search-submit-btn" @click="handleSearch">
            <IconSearch class="text-dark" />
          </button>
        </div>
      </div>
    </div>

    <!-- ローディング -->
    <div v-if="loading" class="spinner-border" role="status">
      <span class="visually-hidden">読み込み中...</span>
    </div>

    <!-- 投稿一覧 -->
    <div v-else>
      <div v-if="posts.length === 0" class="text-center text-muted py-4 mt-5">
        うろ覚えの「うろ」は「おろそか」の「おろ」から変化した語で、<br>「うろうろ」の「うろ」と同じ意味です。たぶん。
      </div>
      <div v-else>
        <div v-for="post in posts" :key="post.id">
          <PostCard :post="post" />
        </div>
      </div>
    </div>

    <!-- もっと読む -->
    <div v-if="nextUrl && !loading" class="mt-4 text-center">
      <button class="btn btn-outline-secondary" @click="handleLoadMore">
        もっと読む
      </button>
    </div>

    <div 
    class="position-fixed bottom-0 end-0 me-2"
    style="margin-bottom: 60px;">
        <button class="btn" @click="openNew">
            <IconCirclePlusFilled class="text-success" :size="60"/>
        </button>  
    </div>    

    <!-- 新規投稿モーダル -->
    <NewPostModal :show="showNewModal" @close="showNewModal = false" @posted="onPosted" />
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.tab-scroll {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.tab-scroll::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.tab-btn {
  border: none;
  background: transparent;
  color: #767676;
  padding: 8px 16px;
  font-size: 16px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #111827;
}

.tab-btn.active {
  color: #111827;
  border-bottom-color: #111827;
}

.sort-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #111827;
  padding: 6px 10px;
  border-radius: 10px;
}

.sort-menu {
  position: absolute;
  right: 0;
  margin-top: 8px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  min-width: 160px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  padding: 6px;
}

.sort-item {
  border: none;
  background: transparent;
  text-align: left;
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 14px;
}

.sort-item:hover {
  background: #f3f4f6;
}

.sort-item.active {
  background: #111827;
  color: #fff;
}

.search-toggle-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #111827;
  padding: 6px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-toggle-btn:hover {
  border-color: #111827;
}

.search-accordion {
  position: absolute;
  top: 100%;
  right: 0;
  width: 100%;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.search-accordion.active {
  max-height: 100px;
}

.search-input {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 14px;
  flex: 1;
}

.search-input:focus {
  outline: none;
  border-color: #111827;
  box-shadow: 0 0 0 2px rgba(17, 24, 39, 0.1);
}

.search-submit-btn {
  padding: 6px 10px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #111827;
  border-radius: 8px;
  cursor: pointer;
  flex-shrink: 0;
}

.card {
  transition: box-shadow 0.3s;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-title {
  margin-bottom: 0.5rem;
}

.card-title a {
  text-decoration: none;
  color: #0d6efd;
}

.card-title a:hover {
  text-decoration: underline;
}
</style>
