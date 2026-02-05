import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// Bootstrap JS（モーダル等使うなら）
import "bootstrap/dist/js/bootstrap.bundle.min.js";

// SCSS（共通スタイル）
import "./assets/styles/assets.scss";

createApp(App).use(router).mount("#app");