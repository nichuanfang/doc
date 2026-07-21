---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "MyDoc"
#  text: ""
  tagline: 个人文档平台
  image:
    src: /logo.svg
    alt: MyDoc Logo
  actions:
    - theme: brand
      text: 快速开始
      link: 面试小抄
    - theme: alt
      text: GitHub 仓库
      link: https://github.com/nichuanfang/doc

features:
  - icon: 📝
    title: 面试/算法复盘
    details: 归纳 LeetCode 经典题解与大厂面试高频考点，构建完整的后端知识脑图。
#    link: /interview 
#    linkText: Go
  - icon: 🛡️
    title: 生产级项目实战
    details: 从 0 到 1 构建高可用系统，涵盖多级缓存、分布式事务（Seata）及限流熔断解决方案。
  - icon: 🐳
    title: 云原生与运维
    details: 玩转 Docker 容器化、K8s 编排架构，以及基于 Jenkins/GitHub Actions 的 CI/CD 自动化流水线。
  - icon: 🧩
    title: 开发规约与治理
    details: 落地阿里 Java 开发手册，集成 Checkstyle/SonarQube 静态扫描，追求代码极致整洁。
  - icon: 🌐
    title: 全栈技术触角
    details: 延伸至 Vue/React 前端工程化，探索 Python 自动化脚本及 Go 微服务，打破技术边界。
  - icon: 📈
    title: 业务深度思考
    details: 沉淀电商、金融或中台业务模型设计，探讨领域驱动设计（DDD）在复杂业务中的落地。
---