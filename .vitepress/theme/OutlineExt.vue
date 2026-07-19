<!-- .vitepress/theme/OutlineExt.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vitepress'

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

let ignoreAutoScroll = false
let pageScrollYAtClick = 0
let pageStable = false
let waitTimer: ReturnType<typeof setTimeout> | null = null
let deferredTimer: ReturnType<typeof setTimeout> | null = null
let routeDeferredTimer: ReturnType<typeof setTimeout> | null = null
let loadCleanup: (() => void) | null = null
let containerEl: HTMLElement | null = null
let rafId: number | null = null   // 新增：用于取消 rAF

const router = useRouter()
const prevOnAfterRouteChange = router.onAfterRouteChange

function doScroll(container: HTMLElement | null, activeLink: HTMLAnchorElement | null) {
  if (!container || !activeLink) return
  const cr = container.getBoundingClientRect()
  const ar = activeLink.getBoundingClientRect()
  if (ar.top < cr.top || ar.bottom > cr.bottom) {
    const relativeTop = ar.top - cr.top + container.scrollTop
    const target = relativeTop - cr.height / 2 + ar.height / 2
    container.scrollTo({ top: Math.max(0, target), behavior: 'smooth' })
  }
}

function syncHash(activeLink: HTMLAnchorElement | null) {
  if (!activeLink) return
  const newHash = activeLink.getAttribute('href')?.replace(/^.*#/, '#') || ''
  if (window.location.hash !== newHash) {
    history.replaceState(null, '', newHash
      ? `${window.location.pathname}${window.location.search}${newHash}`
      : window.location.pathname + window.location.search)
  }
}

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
  containerEl.addEventListener('touchmove', onContainerInteract, { passive: true })
  containerEl.addEventListener('focusin', onContainerInteract)
}

function onScrollAction() {
  const container = document.querySelector<HTMLElement>('.aside-container')
  if (container) syncContainerListeners(container)
  if (ignoreAutoScroll) return
  const activeLink = document.querySelector<HTMLAnchorElement>('.VPDocAsideOutline .outline-link.active')
  doScroll(container, activeLink)
  syncHash(activeLink)
}

const throttledAction = throttle(onScrollAction, 100)

function resetAutoScroll() {
  ignoreAutoScroll = false
  pageStable = false
  pageScrollYAtClick = 0
  if (waitTimer) { clearTimeout(waitTimer); waitTimer = null }
}

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

function onClick(e: MouseEvent) {
  const link = (e.target as HTMLElement).closest<HTMLAnchorElement>('.outline-link')
  if (link) pauseAutoScroll()
}

function onContainerInteract() {
  pauseAutoScroll()
}

function onScroll() {
  if (ignoreAutoScroll) {
    if (pageStable && Math.abs(window.scrollY - pageScrollYAtClick) > 50) {
      ignoreAutoScroll = false
      onScrollAction()
    }
    return
  }
  throttledAction()
}

// ==================== 可取消的等待函数 ====================
function waitForOutlineReady(callback: () => void, maxWait = 400) {
  if (rafId) cancelAnimationFrame(rafId)
  const start = Date.now()
  const check = () => {
    const container = document.querySelector<HTMLElement>('.aside-container')
    const activeLink = document.querySelector<HTMLAnchorElement>('.VPDocAsideOutline .outline-link.active')
    if ((container && activeLink) || Date.now() - start > maxWait) {
      rafId = null
      callback()
    } else {
      rafId = requestAnimationFrame(check)
    }
  }
  check()
}

function cancelWait() {
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
}

// ============================================================
onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onClick)

  router.onAfterRouteChange = (to: string) => {
    prevOnAfterRouteChange?.(to)
    resetAutoScroll()
    cancelWait()
    if (routeDeferredTimer) clearTimeout(routeDeferredTimer)
    routeDeferredTimer = setTimeout(() => waitForOutlineReady(onScrollAction), 30)
  }

  waitForOutlineReady(onScrollAction)

  const onLoad = () => {
    if (deferredTimer) clearTimeout(deferredTimer)
    deferredTimer = setTimeout(() => waitForOutlineReady(onScrollAction), 120)
  }
  if (document.readyState === 'complete') {
    onLoad()
  } else {
    window.addEventListener('load', onLoad, { once: true })
    loadCleanup = () => window.removeEventListener('load', onLoad)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onClick)

  if (containerEl) {
    containerEl.removeEventListener('wheel', onContainerInteract)
    containerEl.removeEventListener('touchstart', onContainerInteract)
    containerEl.removeEventListener('touchmove', onContainerInteract)
    containerEl.removeEventListener('focusin', onContainerInteract)
    containerEl = null
  }

  router.onAfterRouteChange = prevOnAfterRouteChange

  cancelWait()
  if (waitTimer) clearTimeout(waitTimer)
  if (deferredTimer) clearTimeout(deferredTimer)
  if (routeDeferredTimer) clearTimeout(routeDeferredTimer)
  loadCleanup?.()

  waitTimer = deferredTimer = routeDeferredTimer = loadCleanup = null
})
</script>

<template>
  <span style="display: none" />
</template>