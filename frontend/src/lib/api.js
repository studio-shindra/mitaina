import axios from "axios";
import { useRouter } from "vue-router";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

// 401 エラーで自動ログアウト
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // トークンを削除してログインページへ
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/**
 * ページネーション URL が絶対URL でも相対URL でも対応する fetch ユーティリティ
 * @param {string} urlOrPath - 絶対URL または 相対URL (/api/posts/ など)
 * @returns {Promise<Response>}
 */
export const fetchPage = async (urlOrPath) => {
  let url = urlOrPath;
  
  // 絶対URL の場合は path + search のみ抽出
  if (urlOrPath.startsWith("http")) {
    const urlObj = new URL(urlOrPath);
    url = urlObj.pathname + urlObj.search;
  }
  
  return api.get(url);
};

export default api;
