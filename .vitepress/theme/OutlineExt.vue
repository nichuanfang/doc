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
      if (timer) {
        clearTimeout(timer)
        timer = null
      }
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
let deferredTimer: ReturnType<typeof setTimeout> | null = null
let routeDeferredTimer: ReturnType<typeof setTimeout> | null = null
let loadCleanup: (() => void) | null = null

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
    // 使用 getBoundingClientRect + scrollTop 比 offsetTop 更稳健，
    // 不依赖 offsetParent 链条
    const relativeTop = ar.top - cr.top + container.scrollTop
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
  // 没有激活标题时不动 hash，避免覆盖用户手动输入的 hash
  if (!activeLink) return

  const newHash = activeLink.getAttribute('href')?.replace(/^.*#/, '#') || ''

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
  // 防止重复初始化
  if (pollTimer) return

  pollTimer = setInterval(() => {
    const container = document.querySelector('.aside-container')
    if (!container) return

    clearInterval(pollTimer!)
    pollTimer = null

    // --- 绑定事件 ---
    window.addEventListener('scroll', onScroll, { passive: true })
    document.addEventListener('click', onClick, { passive: true })

    // --- 路由切换时重置状态 ---
    router.onAfterRouteChange = () => {
      resetAutoScroll()
      // 路由切换后延迟执行，等新页面 DOM 渲染完成
      if (routeDeferredTimer) clearTimeout(routeDeferredTimer)
      routeDeferredTimer = setTimeout(onScrollAction, 200)
    }

    // --- load 事件：页面完全加载后再校准一次 ---
    const onLoad = () => {
      if (deferredTimer) clearTimeout(deferredTimer)
      deferredTimer = setTimeout(onScrollAction, 500)
    }
    window.addEventListener('load', onLoad, { once: true })
    loadCleanup = () => window.removeEventListener('load', onLoad)

    // --- 初始执行 ---
    if (deferredTimer) clearTimeout(deferredTimer)
    deferredTimer = setTimeout(onScrollAction, 300)
  }, POLL_INTERVAL)
}

// ============================================================
// 生命周期
// ============================================================
onMounted(() => {
  waitForContainer()
})

onUnmounted(() => {
  // 事件监听
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onClick)

  // 路由钩子
  router.onAfterRouteChange = undefined

  // 定时器
  if (waitTimer) clearTimeout(waitTimer)
  if (pollTimer) clearInterval(pollTimer)
  if (deferredTimer) clearTimeout(deferredTimer)
  if (routeDeferredTimer) clearTimeout(routeDeferredTimer)

  // load 事件
  loadCleanup?.()

  // 重置为 null
  waitTimer = null
  pollTimer = null
  deferredTimer = null
  routeDeferredTimer = null
  loadCleanup = null
})
</script>

<template>
  <span style="display: none" />
</template>