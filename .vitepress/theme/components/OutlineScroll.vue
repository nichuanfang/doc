<script setup lang="ts">
import { onMounted, onUnmounted, nextTick } from 'vue'

let observer: MutationObserver | null = null
let asideEl: HTMLElement | null = null

let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null

/** 由代码自身触发滚动时置位，避免把自动滚动误判为用户交互 */
let isAutoScrolling = false
let autoScrollingTimer: ReturnType<typeof setTimeout> | null = null

/** 标记用户正在与 outline 交互，暂时关闭自动滚动 */
function markUserInteraction() {
  if (isAutoScrolling) return

  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  interactionTimer = setTimeout(() => {
    userInteracting = false
    // 解锁后主动补一次纠正，防止交互窗口内的 active 变化被吞掉
    requestAnimationFrame(scrollActiveIntoView)
  }, 1500)
}

/** 将当前 active 的 outline 项滚入可视区域（居中 + 边界钳制，保证可到达顶端/底端） */
function scrollActiveIntoView() {
  if (userInteracting || !asideEl) return

  const active = asideEl.querySelector('.outline-link.active') as HTMLElement | null
  if (!active) return

  const container = asideEl
  const activeTop = active.offsetTop
  const activeHeight = active.offsetHeight
  const containerHeight = container.clientHeight
  const maxScroll = container.scrollHeight - containerHeight

  // 目标：尽量居中，但钳制在 [0, maxScroll]，确保首项可到顶端、末项可到底端
  let target = activeTop - containerHeight / 2 + activeHeight / 2
  target = Math.max(0, Math.min(target, maxScroll))

  // 已在可视区域内则跳过（阈值可按需要微调）
  if (Math.abs(container.scrollTop - target) < 8) return

  isAutoScrolling = true
  if (autoScrollingTimer) clearTimeout(autoScrollingTimer)

  const onScrollEnd = () => {
    isAutoScrolling = false
    container.removeEventListener('scrollend', onScrollEnd)
  }

  container.addEventListener('scrollend', onScrollEnd, { once: true })
  // 兜底：不支持 scrollend 的浏览器用超时
  autoScrollingTimer = setTimeout(onScrollEnd, 800)

  container.scrollTo({
    top: target,
    behavior: 'smooth'
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

    // 只监听真正代表用户手动操作的事件，去掉 scroll，避免自动滚动产生的误判
    ;['wheel', 'touchstart'].forEach((evt) => {
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
    ;['wheel', 'touchstart'].forEach((evt) => {
      asideEl!.removeEventListener(evt, markUserInteraction)
    })
  }
})
</script>

<template>
  <!-- 仅用于挂载逻辑，不渲染可见内容 -->
  <span style="display: none" aria-hidden="true" />
</template>