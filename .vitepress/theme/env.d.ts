// 允许引入 .vue 组件
declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// 允许引入 .css 文件
declare module "*.css" {
  const content: any;
  export default content;
}
