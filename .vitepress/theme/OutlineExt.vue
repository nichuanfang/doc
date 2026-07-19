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
let deferredTimer: ReturnType<typeof setTimeout> | null = null
let routeDeferredTimer: ReturnType<typeof setTimeout> | null = null
let loadCleanup: (() => void) | null = null
let containerEl: HTMLElement | null = null

const router = useRouter()
// 保存原有的路由钩子引用，避免覆盖其他逻辑注册的钩子
const prevOnAfterRouteChange = router.onAfterRouteChange

// ============================================================
// 大纲滚动跟随
// ============================================================
function doScroll(container: HTMLElement | null, activeLink: HTMLAnchorElement | null) {
  if (!container || !activeLink) return

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
// URL hash 同步
// ============================================================
function syncHash(activeLink: HTMLAnchorElement | null) {
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
// 绑定 / 迁移大纲容器上的用户交互监听
// ============================================================
function syncContainerListeners(container: HTMLElement) {
  if (container === containerEl) return

  if (containerEl) {
    containerEl.removeEventListener('wheel', onContainerInteract)
    containerEl.removeEventListener('touchstart', onContainerInteract)
    containerEl.removeEventListener('touchmove', onContainerInteract)
    containerEl.removeEventListener('focusin', onContainerInteract)
  }

  containerEl = container
  containerEl.addEventListener('wheel', onContainerInteract, { passive: true })
  containerEl.addEventListener('touchstart', onContainerInteract, { passive: true })
  // 修复：持续监听 touchmove，让触屏长按滑动时暂停窗口跟着手势持续延长，
  // 避免滑动耗时超过 700ms 导致暂停提前失效
  containerEl.addEventListener('touchmove', onContainerInteract, { passive: true })
  // 修复：监听 focusin，覆盖键盘 / 屏幕阅读器用户 Tab 到大纲链接时
  // 浏览器原生的“聚焦滚动”，避免被自动纠正打断
  containerEl.addEventListener('focusin', onContainerInteract)
}

// ============================================================
// 节流后的复合动作
// ============================================================
function onScrollAction() {
  const container = document.querySelector<HTMLElement>('.aside-container')
  if (container) syncContainerListeners(container)

  if (ignoreAutoScroll) return

  const activeLink = document.querySelector<HTMLAnchorElement>(
    '.VPDocAsideOutline .outline-link.active'
  )
  doScroll(container, activeLink)
  syncHash(activeLink)
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
// 暂停自动跟随（点击大纲链接 / 手动滚动大纲容器 / 键盘聚焦 都会触发）
// ============================================================
function pauseAutoScroll() {
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
// 点击大纲 → 暂停
// ============================================================
function onClick(e: MouseEvent) {
  const link = (e.target as HTMLElement).closest<HTMLAnchorElement>('.outline-link')
  if (!link) return

  pauseAutoScroll()
}

// ============================================================
// 用户直接与大纲容器交互（滚轮 / 触摸拖动 / 键盘聚焦）→ 暂停
// 根因：滚动到大纲顶部/底部边界时，浏览器会把多余的滚动量顺延链式
// 传递给 window，触发 window scroll 监听器进而把大纲“纠正”回原位置。
// ============================================================
function onContainerInteract() {
  pauseAutoScroll()
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
// 生命周期
// ============================================================
onMounted(() => {
  // 绑定全局监听：不依赖大纲容器是否已经存在于 DOM 中，
  // onScrollAction 内部会自行判断容器/激活链接是否存在
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onClick)

  // --- 路由切换时重置状态 ---
  // 链式调用，先执行原有钩子，再执行自己的逻辑，避免覆盖其他注册者
  router.onAfterRouteChange = (to: string) => {
    prevOnAfterRouteChange?.(to)
    resetAutoScroll()
    // 路由切换后延迟执行，等新页面 DOM 渲染完成
    // （同时会顺带检测并重新绑定新页面的大纲容器）
    if (routeDeferredTimer) clearTimeout(routeDeferredTimer)
    routeDeferredTimer = setTimeout(onScrollAction, 200)
  }

  // --- 初始执行（等待首屏渲染稳定）---
  deferredTimer = setTimeout(onScrollAction, 300)

  // --- 页面完全加载后再校准一次 ---
  const onLoad = () => {
    if (deferredTimer) clearTimeout(deferredTimer)
    deferredTimer = setTimeout(onScrollAction, 500)
  }
  if (document.readyState === 'complete') {
    // 修复：组件挂载时 load 事件可能早已触发过（例如脚本异步加载），
    // 此时再监听 'load' 永远不会响应，需要立即执行一次校准兜底
    onLoad()
  } else {
    window.addEventListener('load', onLoad, { once: true })
    loadCleanup = () => window.removeEventListener('load', onLoad)
  }
})

onUnmounted(() => {
  // 事件监听
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onClick)
  if (containerEl) {
    containerEl.removeEventListener('wheel', onContainerInteract)
    containerEl.removeEventListener('touchstart', onContainerInteract)
    containerEl.removeEventListener('touchmove', onContainerInteract)
    containerEl.removeEventListener('focusin', onContainerInteract)
    containerEl = null
  }

  // 路由钩子：恢复为组件挂载前的原始值，而不是直接置空
  router.onAfterRouteChange = prevOnAfterRouteChange

  // 定时器
  if (waitTimer) clearTimeout(waitTimer)
  if (deferredTimer) clearTimeout(deferredTimer)
  if (routeDeferredTimer) clearTimeout(routeDeferredTimer)

  // load 事件
  loadCleanup?.()

  // 重置为 null
  waitTimer = null
  deferredTimer = null
  routeDeferredTimer = null
  loadCleanup = null
})
</script>

<template>
  <span style="display: none" />
</template>