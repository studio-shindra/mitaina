<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../lib/api";

const route = useRoute();
const router = useRouter();
const post = ref(null);
const loading = ref(true);
const error = ref("");
const userReactions = ref({});
const showReportForm = ref(false);
const reportReason = ref("spam");
const reportMessage = ref("");
const isFollowing = ref(false);

const loadPost = async () => {
  try {
    const postId = route.params.id;
    const response = await api.get(`/posts/${postId}/`);
    post.value = response.data;
  } catch (err) {
    error.value = "投稿が見つかりません";
  }
};

// ユーザーの反応を確認
const loadUserReactions = async () => {
  try {
    const responses = await Promise.all([
      api.get(`/me/reactions/?type=like`),
      api.get(`/me/reactions/?type=hatena`),
      api.get(`/me/reactions/?type=correct`),
      api.get(`/me/reactions/?type=collect`),
    ]);

    const postId = route.params.id;
    responses.forEach((res, idx) => {
      const reactionTypes = ["like", "hatena", "correct", "collect"];
      const type = reactionTypes[idx];
      userReactions.value[type] = res.data.results?.some(
        (r) => r.post.id === postId
      ) || false;
    });
  } catch (err) {
    // ユーザーがログインしていない場合は無視
  }
};

// フォロー状態を確認
const loadFollowStatus = async () => {
  try {
    if (post.value?.author?.username) {
      const response = await api.get(`/users/${post.value.author.username}/`);
      isFollowing.value = response.data.is_followed;
    }
  } catch (err) {
    // 無視
  }
};

const toggleReaction = async (reactionType) => {
  try {
    const postId = route.params.id;
    
    // UI を即時更新（楽観的更新）
    const wasReacted = userReactions.value[reactionType];
    userReactions.value[reactionType] = !wasReacted;
    
    const oldCount = post.value[`${reactionType}_count`] || 0;
    post.value[`${reactionType}_count`] = wasReacted ? oldCount - 1 : oldCount + 1;
    
    try {
      // API 呼び出し
      const response = await api.post(`/posts/${postId}/react/`, {
        reaction_type: reactionType,
      });
      
      // 成功時は投稿を再fetch して正確な値を反映
      await loadPost();
      await loadUserReactions();
    } catch (err) {
      // エラー時は UI をロールバック
      userReactions.value[reactionType] = wasReacted;
      post.value[`${reactionType}_count`] = oldCount;
      error.value = "反応の登録に失敗しました";
    }
  } catch (err) {
    error.value = "反応の登録に失敗しました";
  }
};

const toggleFollow = async () => {
  try {
    if (post.value?.author?.username) {
      await api.post(`/users/${post.value.author.username}/follow/`);
      isFollowing.value = !isFollowing.value;
    }
  } catch (err) {
    error.value = "フォロー処理に失敗しました";
  }
};

const submitReport = async () => {
  try {
    const postId = route.params.id;
    await api.post(`/posts/${postId}/report/`, {
      reason: reportReason.value,
      message: reportMessage.value || null,
    });
    showReportForm.value = false;
    error.value = "";
    alert("報告ありがとうございました");
  } catch (err) {
    error.value = "報告の送信に失敗しました";
  }
};

const shareOnX = () => {
  if (!post.value) return;

  let shareText = post.value.text;
  if (post.value.work_title) shareText += `\n── ${post.value.work_title}`;
  if (post.value.performer_name) shareText += `\n── ${post.value.performer_name}`;
  if (post.value.character_name) shareText += `\n── ${post.value.character_name}`;
  shareText += "\n#MITAINA";

  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
  window.open(url, "_blank");
};

const goToUserProfile = () => {
  if (post.value?.author?.username) {
    router.push(`/u/${post.value.author.username}`);
  }
};

onMounted(async () => {
  loading.value = true;
  await loadPost();
  await Promise.all([loadUserReactions(), loadFollowStatus()]);
  loading.value = false;
});
</script>

<template>
  <div class="post-detail-container">
    <div class="card mx-auto" style="max-width: 700px">
      <div class="card-body">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <template v-else>
          <div v-if="post">
            <!-- 投稿情報ヘッダー -->
            <div class="mb-4 pb-3 border-bottom">
              <h3 class="mb-2">{{ post.text }}</h3>
              <div
                class="d-flex justify-content-between align-items-center"
                @click="goToUserProfile"
                style="cursor: pointer"
              >
                <div>
                  <strong>{{ post.author.username }}</strong>
                  <br />
                  <small class="text-muted">@{{ post.author.handle_name }}</small>
                </div>
              </div>
            </div>

            <!-- メタ情報 -->
            <div class="mb-4 p-3 bg-light rounded">
              <div class="mb-2">
                <strong>ジャンル:</strong> {{ post.genre }}
              </div>
              <div v-if="post.work_title" class="mb-2">
                <strong>作品:</strong> {{ post.work_title }}
              </div>
              <div v-if="post.performer_name" class="mb-2">
                <strong>出演者:</strong> {{ post.performer_name }}
              </div>
              <div v-if="post.character_name" class="mb-2">
                <strong>役名:</strong> {{ post.character_name }}
              </div>
              <small class="text-muted">
                投稿日: {{ new Date(post.created_at).toLocaleString("ja-JP") }}
              </small>
            </div>

            <!-- 反応ボタン -->
            <div class="d-grid gap-2 mb-3">
              <button
                @click="toggleReaction('like')"
                class="btn"
                :class="
                  userReactions.like
                    ? 'btn-primary'
                    : 'btn-outline-primary'
                "
              >
                <strong>いいね</strong> ({{ post.like_count || 0 }})
              </button>
              <button
                @click="toggleReaction('hatena')"
                class="btn"
                :class="
                  userReactions.hatena
                    ? 'btn-warning'
                    : 'btn-outline-warning'
                "
              >
                <strong>いやちゃうやろw</strong> ({{ post.hatena_count || 0 }})
              </button>
              <button
                @click="toggleReaction('correct')"
                class="btn"
                :class="
                  userReactions.correct
                    ? 'btn-success'
                    : 'btn-outline-success'
                "
              >
                <strong>なるほど</strong> ({{ post.correct_count || 0 }})
              </button>
              <button
                @click="toggleReaction('collect')"
                class="btn"
                :class="
                  userReactions.collect
                    ? 'btn-secondary'
                    : 'btn-outline-secondary'
                "
              >
                <strong>コレクト</strong> ({{ post.collect_count || 0 }})
              </button>
            </div>

            <!-- フォローボタン -->
            <button
              @click="toggleFollow"
              class="btn w-100 mb-3"
              :class="isFollowing ? 'btn-outline-primary' : 'btn-primary'"
            >
              {{ isFollowing ? "フォロー中" : "フォローする" }}
            </button>

            <!-- X シェアボタン -->
            <button
              @click="shareOnX"
              class="btn btn-info w-100 mb-3"
            >
              𝕏で共有
            </button>

            <!-- 報告ボタン -->
            <button
              @click="showReportForm = !showReportForm"
              class="btn btn-outline-danger w-100 mb-3"
            >
              報告する
            </button>

            <!-- 報告フォーム -->
            <div v-if="showReportForm" class="card bg-danger-light mb-3">
              <div class="card-body">
                <h6 class="card-title">報告理由を選択してください</h6>
                <div class="mb-3">
                  <select v-model="reportReason" class="form-select">
                    <option value="spam">スパム</option>
                    <option value="inappropriate">不適切なコンテンツ</option>
                    <option value="quote">引用元の権利問題</option>
                    <option value="other">その他</option>
                  </select>
                </div>
                <div class="mb-3">
                  <textarea
                    v-model="reportMessage"
                    class="form-control"
                    rows="3"
                    placeholder="詳細（任意）"
                  ></textarea>
                </div>
                <button
                  @click="submitReport"
                  class="btn btn-danger me-2"
                >
                  報告する
                </button>
                <button
                  @click="showReportForm = false"
                  class="btn btn-secondary"
                >
                  キャンセル
                </button>
              </div>
            </div>

            <!-- ホームに戻るボタン -->
            <router-link to="/" class="btn btn-outline-secondary w-100">
              ホームに戻る
            </router-link>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-detail-container {
  max-width: 700px;
  margin: 0 auto;
}

.btn-info {
  background-color: #17a2b8;
  border-color: #17a2b8;
}

.btn-info:hover {
  background-color: #138496;
  border-color: #117a8b;
}
</style>
