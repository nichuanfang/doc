import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "DocSite",
  description: "A VitePress Site",
  cleanUrls: true,
  lastUpdated: true,
  appearance: true,
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: "Home", link: "/" },
      { text: "Examples", link: "/markdown-examples" },
    ],
    sidebar: [
      {
        text: "Examples",
        items: [
          { text: "Markdown Examples", link: "/markdown-examples" },
          { text: "Runtime API Examples", link: "/api-examples" },
        ],
      },
    ],
    editLink: {
      pattern: "https://github.com/nichuanfang/doc/edit/main/:path",
      text: "在 GitHub 上编辑此页",
    },
    // 自定义最后更新时间的文本显示
    lastUpdated: {
      text: "最后更新于",
      formatOptions: {
        dateStyle: "full",
        timeStyle: "medium",
      },
    },
    socialLinks: [
      { icon: "github", link: "https://github.com/nichuanfang/nichuanfang" },
    ],
    search: {
      provider: "local",
      options: {
        locales: {
          root: {
            translations: {
              button: { buttonText: "搜索文档", buttonAriaLabel: "搜索文档" },
              modal: {
                noResultsText: "无法找到相关结果",
                footer: { selectText: "选择", navigateText: "切换" },
              },
            },
          },
        },
        // 强烈建议：显示详细摘要，方便用户在搜索列表中直接看到上下文
        detailedView: true,
      },
    },
    // footer: {
    //   message: "基于 MIT 许可发布",
    //   copyright: `版权所有 © 2026-${new Date().getFullYear()} chuanfang`,
    // },
  },
  markdown: {
    // 建议 3: 显示行号
    lineNumbers: true,
    // 建议 4: 配置代码块的主题（深色/浅色自动切换）
    theme: {
      light: "github-light",
      dark: "github-dark",
    },

    // 建议 5: 启用数学公式支持 (需要安装 markdown-it-mathjax3)
    math: true,
  },
});
