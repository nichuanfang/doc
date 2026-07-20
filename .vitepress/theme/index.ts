// https://vitepress.dev/guide/custom-theme
import { h } from "vue";
import type { Theme } from "vitepress";
import DefaultTheme from "vitepress/theme-without-fonts";
import OutlineExt from "./OutlineExt.vue";
import "./style.css";
import { routeChangeSignal } from "./routeSignal";

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      "aside-outline-before": () => h(OutlineExt),
    });
  },
  enhanceApp({ router }) {
    const originalAfter = router.onAfterRouteChange;
    router.onAfterRouteChange = (to: string) => {
      originalAfter?.(to);
      routeChangeSignal.value++;
    };
  },
} satisfies Theme;
