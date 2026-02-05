import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// Bootstrap CSS
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap JS（モーダル等使うなら）
import "bootstrap/dist/js/bootstrap.bundle.min.js";

createApp(App).use(router).mount("#app");