<script setup lang="ts">
import { onMounted, onUnmounted, nextTick } from 'vue'

let observer: MutationObserver | null = null
let asideEl: HTMLElement | null = null
let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null

/** 标记用户正在与 outline 交互，暂时关闭自动滚动 */
function markUserInteraction() {
  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  interactionTimer = setTimeout(() => {
    userInteracting = false
  }, 1500)
}

/** 将当前 active 的 outline 项滚入可视区域（双向对称） */
function scrollActiveIntoView() {
  if (userInteracting || !asideEl) return

  const active = asideEl.querySelector(
    '.outline-link.active'
  ) as HTMLElement | null
  if (!active) return

  const container = asideEl
  const cRect = container.getBoundingClientRect()
  const aRect = active.getBoundingClientRect()

  // 只有当 active 项有任意部分超出可视区域时才滚动
  const isAbove = aRect.top < cRect.top + 8
  const isBelow = aRect.bottom > cRect.bottom - 8

  if (!isAbove && !isBelow) return

  active.scrollIntoView({
    behavior: 'smooth',
    block: 'center',   // 上下方向行为对称
    inline: 'nearest'
  })
}

/** 延迟兜底，用于刷新 / 滚动恢复 / bfcache 场景 */
function restore() {
  setTimeout(() => {
    requestAnimationFrame(scrollActiveIntoView)
  }, 120)
}

onMounted(() => {
  nextTick(() => {
    asideEl = document.querySelector('.aside-container') as HTMLElement | null
    if (!asideEl) return

    // 监听用户在 outline 上的交互
    ;['wheel', 'touchstart', 'pointerdown', 'mouseenter'].forEach((evt) => {
      asideEl!.addEventListener(evt, markUserInteraction, { passive: true })
    })

    // 监听 active 类变化
    observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (
          m.type === 'attributes' &&
          m.attributeName === 'class' &&
          (m.target as HTMLElement).classList.contains('active')
        ) {
          requestAnimationFrame(scrollActiveIntoView)
          break
        }
      }
    })

    observer.observe(asideEl, {
      attributes: true,
      attributeFilter: ['class'],
      subtree: true
    })

    // 初次定位
    restore()

    // 浏览器滚动恢复后通常会触发一次 scroll，再补一次
    window.addEventListener(
      'scroll',
      () => {
        restore()
      },
      { once: true, passive: true }
    )

    // bfcache（前进 / 后退）恢复
    window.addEventListener('pageshow', (e) => {
      if (e.persisted) restore()
    })
  })
})

onUnmounted(() => {
  observer?.disconnect()
  if (interactionTimer) clearTimeout(interactionTimer)
  if (asideEl) {
    ;['wheel', 'touchstart', 'pointerdown', 'mouseenter'].forEach((evt) => {
      asideEl!.removeEventListener(evt, markUserInteraction)
    })
  }
})
</script>

<template>
  <!-- 仅用于挂载逻辑，不渲染可见内容 -->
  <span style="display: none" aria-hidden="true" />
</template>