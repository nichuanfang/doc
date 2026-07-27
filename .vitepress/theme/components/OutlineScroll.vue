<script setup lang="ts">
import { onMounted, onUnmounted, onUpdated, nextTick } from 'vue'
import { useLayout } from 'vitepress/theme'

// ===== 可调常量 =====
const INTERACTION_LOCK_MS = 1000
const SCROLL_THRESHOLD_PX = 30
const EDGE_PADDING_PX = 16
const OBSERVER_DEBOUNCE_MS = 30

const { hasAside } = useLayout() 

let asideEl: HTMLElement | null = null
let observer: MutationObserver | null = null
let abortController: AbortController | null = null

let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null
let observerTimer: ReturnType<typeof setTimeout> | null = null

let isMounted = false

// ===== 辅助函数 =====

function markUserInteraction() {
  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  interactionTimer = setTimeout(() => {
    userInteracting = false
  }, INTERACTION_LOCK_MS)
}

function isLastOutlineLink(el: HTMLElement, container: HTMLElement): boolean {
  const allLinks = container.querySelectorAll('.outline-link')
  return allLinks.length > 0 && el === allLinks[allLinks.length - 1]
}

function isFirstOutlineLink(el: HTMLElement, container: HTMLElement): boolean {
  const allLinks = container.querySelectorAll('.outline-link')
  return allLinks.length > 0 && el === allLinks[0]
}

function scrollToTop() {
  if (!asideEl || userInteracting) return
  if (Math.abs(asideEl.scrollTop) < SCROLL_THRESHOLD_PX) return
  asideEl.scrollTo({ top: 0, behavior: 'auto' })
}

function scrollActiveIntoView() {
  if (!hasAside.value || userInteracting || !asideEl) return

  const active = asideEl.querySelector('.outline-link.active') as HTMLElement | null

  // 页面在顶部时 VitePress 会移除 active → 滚动 outline 到顶部
  if (!active) {
    scrollToTop()
    return
  }

  const container = asideEl
  const cRect = container.getBoundingClientRect()
  const aRect = active.getBoundingClientRect()
  const containerHeight = container.clientHeight
  const maxScroll = Math.max(0, container.scrollHeight - containerHeight)

  const relativeTop = aRect.top - cRect.top
  const relativeBottom = aRect.bottom - cRect.top
  const isAbove = relativeTop < 0
  const isBelow = relativeBottom > containerHeight

  if (!isAbove && !isBelow) return

  let target = container.scrollTop
  if (isAbove) {
    target = container.scrollTop + relativeTop - EDGE_PADDING_PX
  } else {
    target = container.scrollTop + relativeBottom - containerHeight + EDGE_PADDING_PX
  }

  if (isFirstOutlineLink(active, container)) target = 0
  if (isLastOutlineLink(active, container)) target = maxScroll

  target = Math.max(0, Math.min(target, maxScroll))
  if (Math.abs(container.scrollTop - target) < SCROLL_THRESHOLD_PX) return

  container.scrollTo({ top: target, behavior: 'auto' })
}

function restore() {
  requestAnimationFrame(scrollActiveIntoView)
}

function onActiveChanged() {
  if (observerTimer) clearTimeout(observerTimer)
  observerTimer = setTimeout(() => {
    if (!isMounted) return
    requestAnimationFrame(scrollActiveIntoView)
  }, OBSERVER_DEBOUNCE_MS)
}

function reconnectObserver() {
  const newAside = document.querySelector('.aside-container') as HTMLElement | null
  if (newAside && newAside !== asideEl) {
    asideEl = newAside
    observer?.disconnect()
    observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        const target = m.target as HTMLElement
        if (
          m.type === 'attributes' &&
          m.attributeName === 'class' &&
          target.classList.contains('outline-link')
        ) {
          onActiveChanged()
          break
        }
      }
    })
    observer.observe(asideEl, {
      attributes: true,
      attributeFilter: ['class'],
      subtree: true
    })
    restore()
  }
}

// ===== 生命周期 =====

onMounted(() => {
  isMounted = true
  nextTick(setup)
})

onUpdated(() => {
  nextTick(() => {
    if (isMounted) reconnectObserver()
  })
})

function setup() {
  if (!isMounted) return

  asideEl = document.querySelector('.aside-container') as HTMLElement | null
  if (!asideEl) return

  abortController = new AbortController()
  const { signal } = abortController

    ;['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach((evt) => {
      asideEl!.addEventListener(evt, markUserInteraction, { passive: true, signal })
    })

  observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      const target = m.target as HTMLElement
      if (
        m.type === 'attributes' &&
        m.attributeName === 'class' &&
        target.classList.contains('outline-link')
      ) {
        onActiveChanged()
        break
      }
    }
  })

  observer.observe(asideEl, {
    attributes: true,
    attributeFilter: ['class'],
    subtree: true
  })

  restore()

  // bfcache
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) restore()
  }, { signal })
}

onUnmounted(() => {
  isMounted = false
  observer?.disconnect()
  observer = null
  abortController?.abort()
  abortController = null
  if (interactionTimer) clearTimeout(interactionTimer)
  if (observerTimer) clearTimeout(observerTimer)
  asideEl = null
})
</script>

<template>
</template>