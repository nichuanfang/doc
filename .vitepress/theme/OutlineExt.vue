<!-- .vitepress/theme/OutlineExt.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vitepress'

const router = useRouter()
const prevOnAfterRouteChange = router.onAfterRouteChange

// ==================== 状态变量 ====================
let lastActiveHref = ''                    // 记录上一次高亮的链接 href，用于判断是否真正变化
let userInteracting = false                // 用户是否正在操作大纲（滚轮/触摸）
let interactTimer: ReturnType<typeof setTimeout> | null = null
let observer: MutationObserver | null = null
let containerEl: HTMLElement | null = null

// ==================== 核心功能函数 ====================

/**
 * 将当前高亮的链接滚动到大纲容器的中间位置
 */
function doScroll(container: HTMLElement | null, activeLink: HTMLAnchorElement | null) {
  if (!container || !activeLink) return

  const cr = container.getBoundingClientRect()
  const ar = activeLink.getBoundingClientRect()

  // 只有当 active 链接不在可视区域时才滚动
  if (ar.top < cr.top || ar.bottom > cr.bottom) {
    const relativeTop = ar.top - cr.top + container.scrollTop
    const target = relativeTop - cr.height / 2 + ar.height / 2
    container.scrollTo({ top: Math.max(0, target), behavior: 'smooth' })
  }
}

/**
 * 同步 URL hash（可选功能）
 */
function syncHash(activeLink: HTMLAnchorElement | null) {
  if (!activeLink) return
  const newHash = activeLink.getAttribute('href')?.replace(/^.*#/, '#') || ''
  if (window.location.hash !== newHash) {
    history.replaceState(null, '', newHash
      ? `${window.location.pathname}${window.location.search}${newHash}`
      : window.location.pathname + window.location.search)
  }
}

/**
 * 暂停自动滚动（用户操作大纲时触发）
 */
function pauseAutoScroll() {
  userInteracting = true
  if (interactTimer) clearTimeout(interactTimer)
  interactTimer = setTimeout(() => {
    userInteracting = false
  }, 1200) // 用户停止操作 1.2 秒后恢复自动滚动
}

/**
 * 为大纲容器绑定用户交互监听
 */
function setupContainerListeners(container: HTMLElement) {
  if (container === containerEl) return

  // 清理旧监听
  if (containerEl) {
    containerEl.removeEventListener('wheel', pauseAutoScroll)
    containerEl.removeEventListener('touchstart', pauseAutoScroll)
    containerEl.removeEventListener('touchmove', pauseAutoScroll)
  }

  containerEl = container
  container.addEventListener('wheel', pauseAutoScroll, { passive: true })
  container.addEventListener('touchstart', pauseAutoScroll, { passive: true })
  container.addEventListener('touchmove', pauseAutoScroll, { passive: true })
}

/**
 * 检查并执行自动滚动（核心逻辑）
 * 只有当高亮链接真正变化且用户未操作时才执行
 */
function checkAndScroll() {
  const container = document.querySelector<HTMLElement>('.aside-container')
  const activeLink = document.querySelector<HTMLAnchorElement>('.VPDocAsideOutline .outline-link.active')

  if (container) setupContainerListeners(container)

  const currentHref = activeLink?.getAttribute('href') || ''

  if (currentHref && currentHref !== lastActiveHref && !userInteracting) {
    lastActiveHref = currentHref
    doScroll(container, activeLink)
    syncHash(activeLink)
  }
}

/**
 * 路由变化后的处理
 */
function handleRouteChange() {
  lastActiveHref = ''
  userInteracting = false
  setTimeout(checkAndScroll, 60)
}

// ==================== 生命周期 ====================

onMounted(() => {
  // 1. 监听路由变化
  router.onAfterRouteChange = (to: string) => {
    prevOnAfterRouteChange?.(to)
    handleRouteChange()
  }

  // 2. 使用 MutationObserver 监听 active class 变化（最优雅的方式）
  observer = new MutationObserver(checkAndScroll)
  const outline = document.querySelector('.VPDocAsideOutline')
  if (outline) {
    observer.observe(outline, {
      attributes: true,
      subtree: true,
      attributeFilter: ['class']
    })
  }

  // 3. 初始化执行一次
  setTimeout(checkAndScroll, 100)
})

onUnmounted(() => {
  // 清理 MutationObserver
  if (observer) {
    observer.disconnect()
    observer = null
  }

  // 清理定时器
  if (interactTimer) {
    clearTimeout(interactTimer)
    interactTimer = null
  }

  // 清理容器事件监听
  if (containerEl) {
    containerEl.removeEventListener('wheel', pauseAutoScroll)
    containerEl.removeEventListener('touchstart', pauseAutoScroll)
    containerEl.removeEventListener('touchmove', pauseAutoScroll)
    containerEl = null
  }

  // 恢复原始路由钩子
  router.onAfterRouteChange = prevOnAfterRouteChange
})
</script>

<template>
  <span style="display: none" />
</template>