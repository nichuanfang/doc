<!-- .vitepress/theme/OutlineExt.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vitepress'

// ============================================================
// 工具：轻量 throttle
// ============================================================
function throttle(fn: () => void, delay: number) {
  let last = 0
  let timer: ReturnType<typeof setTimeout> | null = null
  return () => {
    const now = Date.now()
    const remaining = delay - (now - last)
    if (remaining <= 0) {
      if (timer) { clearTimeout(timer); timer = null }
      last = now
      fn()
    } else if (!timer) {
      timer = setTimeout(() => {
        last = Date.now()
        timer = null
        fn()
      }, remaining)
    }
  }
}

// ============================================================
// 状态
// ============================================================
let ignoreAutoScroll = false
let pageScrollYAtClick = 0
let pageStable = false
let waitTimer: ReturnType<typeof setTimeout> | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null
let observerReady = false
const POLL_INTERVAL = 60

const router = useRouter()

// ============================================================
// 1) 大纲滚动跟随
// ============================================================
function doScroll() {
  if (ignoreAutoScroll) return

  const activeLink = document.querySelector<HTMLAnchorElement>(
    '.VPDocAsideOutline .outline-link.active'
  )
  if (!activeLink) return

  const container = document.querySelector<HTMLElement>('.aside-container')
  if (!container) return

  const cr = container.getBoundingClientRect()
  const ar = activeLink.getBoundingClientRect()

  if (ar.top < cr.top || ar.bottom > cr.bottom) {
    const relativeTop = activeLink.offsetTop - container.offsetTop
    const target = relativeTop - cr.height / 2 + ar.height / 2
    container.scrollTo({
      top: Math.max(0, target),
      behavior: 'smooth',
    })
  }
}

// ============================================================
// 2) URL hash 同步
// ============================================================
function syncHash() {
  if (ignoreAutoScroll) return

  const activeLink = document.querySelector<HTMLAnchorElement>(
    '.VPDocAsideOutline .outline-link.active'
  )

  // 页面顶部（无标题）→ 清除 hash；有标题 → 更新 hash
  const newHash = activeLink?.getAttribute('href')?.replace(/^.*#/, '#') || ''

  if (window.location.hash !== newHash) {
    history.replaceState(
      null,
      '',
      newHash
        ? `${window.location.pathname}${window.location.search}${newHash}`
        : window.location.pathname + window.location.search
    )
  }
}

// ============================================================
// 节流后的复合动作
// ============================================================
function onScrollAction() {
  doScroll()
  syncHash()
}

const throttledAction = throttle(onScrollAction, 100)

// ============================================================
// 重置自动滚动状态（路由切换时调用）
// ============================================================
function resetAutoScroll() {
  ignoreAutoScroll = false
  pageStable = false
  pageScrollYAtClick = 0
  if (waitTimer) {
    clearTimeout(waitTimer)
    waitTimer = null
  }
}

// ============================================================
// 点击大纲 → 暂停
// ============================================================
function onClick(e: MouseEvent) {
  const link = (e.target as HTMLElement).closest<HTMLAnchorElement>('.outline-link')
  if (!link) return

  ignoreAutoScroll = true
  pageStable = false
  pageScrollYAtClick = window.scrollY

  if (waitTimer) clearTimeout(waitTimer)
  waitTimer = setTimeout(() => {
    pageStable = true
    pageScrollYAtClick = window.scrollY
  }, 700)
}

// ============================================================
// scroll 事件
// ============================================================
function onScroll() {
  if (ignoreAutoScroll) {
    if (pageStable && Math.abs(window.scrollY - pageScrollYAtClick) > 50) {
      ignoreAutoScroll = false
      // 恢复后立即执行一次（不等待节流）
      onScrollAction()
    }
    return
  }
  throttledAction()
}

// ============================================================
// 等待容器 + 绑定事件
// ============================================================
function waitForContainer() {
  if (observerReady) return

  pollTimer = setInterval(() => {
    const container = document.querySelector('.aside-container')
    if (!container) return

    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
    observerReady = true

    window.addEventListener('scroll', onScroll, { passive: true })
    document.addEventListener('click', onClick, { passive: true })

    // 路由切换时重置状态
    router.onAfterRouteChange?.(() => {
      resetAutoScroll()
      setTimeout(onScrollAction, 200)
    })

    setTimeout(onScrollAction, 300)
  }, POLL_INTERVAL)
}

// ============================================================
// 生命周期
// ============================================================
onMounted(() => {
  waitForContainer()
  window.addEventListener('load', () => setTimeout(onScrollAction, 500), { once: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onClick)
  if (waitTimer) clearTimeout(waitTimer)
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <span style="display: none" />
</template>