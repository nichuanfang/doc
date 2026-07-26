<script setup lang="ts">
import { onMounted, onUnmounted, nextTick } from 'vue'

let observer: MutationObserver | null = null
let asideEl: HTMLElement | null = null

let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null

/** 由代码自身触发 scrollIntoView 时置位，避免把"自动滚动"误判为"用户交互" */
let isAutoScrolling = false
let autoScrollingTimer: ReturnType<typeof setTimeout> | null = null

/** 标记用户正在与 outline 交互，暂时关闭自动滚动 */
function markUserInteraction() {
  // 如果这次 scroll/wheel 是我们自己代码触发的，不算用户交互
  if (isAutoScrolling) return

  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  interactionTimer = setTimeout(() => {
    userInteracting = false
    // 关键修复：解锁后主动补一次纠正，
    // 避免用户交互窗口期间发生的 active 变化被吞掉，导致停在中途上不去/下不来
    requestAnimationFrame(scrollActiveIntoView)
  }, 1500)
}

/** 将当前 active 的 outline 项滚入可视区域（双向对称） */
function scrollActiveIntoView() {
  if (userInteracting || !asideEl) return
  const active = asideEl.querySelector('.outline-link.active') as HTMLElement | null
  if (!active) return

  const cRect = asideEl.getBoundingClientRect()
  const aRect = active.getBoundingClientRect()
  const isAbove = aRect.top < cRect.top + 8
  const isBelow = aRect.bottom > cRect.bottom - 8
  if (!isAbove && !isBelow) return

  isAutoScrolling = true

  const onScrollEnd = () => {
    isAutoScrolling = false
    asideEl?.removeEventListener('scrollend', onScrollEnd)
  }
  asideEl.addEventListener('scrollend', onScrollEnd, { once: true })
  // 兜底：不支持 scrollend 的浏览器用超时兜住
  setTimeout(onScrollEnd, 800)

  active.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
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

    // 只监听真正代表"用户在手动滚动/触摸/拖拽 outline"的事件，
    // 去掉 mouseenter（鼠标划过不代表用户想操作它），
    // 去掉 pointerdown（按下不等于滚动，容易被路过的点击误伤）
    ;['wheel', 'touchstart', 'scroll'].forEach((evt) => {
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
  if (autoScrollingTimer) clearTimeout(autoScrollingTimer)
  if (asideEl) {
    ;['wheel', 'touchstart', 'scroll'].forEach((evt) => {
      asideEl!.removeEventListener(evt, markUserInteraction)
    })
  }
})
</script>

<template>
  <!-- 仅用于挂载逻辑，不渲染可见内容 -->
  <span style="display: none" aria-hidden="true" />
</template>