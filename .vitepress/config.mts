import { defineConfig } from 'vitepress'
import { generateSidebar } from 'vitepress-sidebar';

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "MyDOC",
  description: "Doc Site",
  cleanUrls: true,
  lastUpdated: true,
  appearance: "dark",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: "Home", link: "/" },
      { text: "Interview", link: "/interview" },
    ],
    sidebar: generateSidebar([
      {
        /* 这里的配置针对你的文档根目录 */
        documentRootPath: 'interview', // 你的 markdown 所在目录
        // scanStartPath: '',   // (可选) 如果你想针对 guide 文件夹生成
        resolvePath: '/interview/',   // 基础路径前缀
        useTitleFromFileHeading: true, // 使用 md 文件里的第一个一级标题作为菜单名
        collapsed: true,          // 默认是否折叠
        hyphenToSpace: true,      // 将连字符转换为空格
        undescendingOrder: false, // 是否降序排列
      },
      // 如果有其他目录，可以继续添加对象
    ]),
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
