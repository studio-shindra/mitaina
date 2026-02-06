import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import NewPost from "../views/NewPost.vue";
import Me from "../views/Me.vue";
import PostDetail from "../views/PostDetail.vue";
import UserProfile from "../views/UserProfile.vue";
import PasswordReset from "../views/PasswordReset.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/password-reset", component: PasswordReset },
  { path: "/new", component: NewPost, meta: { requiresAuth: true } },
  { path: "/me", component: Me, meta: { requiresAuth: true } },
  { path: "/p/:id", component: PostDetail },
  { path: "/u/:username", component: UserProfile },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 認証ガード
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else {
    next();
  }
});

export default router;