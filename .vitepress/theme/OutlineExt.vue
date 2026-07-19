<!-- .vitepress/theme/OutlineExt.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

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

const scrollToActiveOutline = throttle(() => {
  // 找到当前激活的大纲链接
  const activeLink = document.querySelector<HTMLAnchorElement>(
    '.VPDocAsideOutline .outline-link.active'
  )
  if (!activeLink) return

  // 找到实际的滚动容器
  const container = document.querySelector<HTMLElement>('.aside-container')
  if (!container) return

  const containerRect = container.getBoundingClientRect()
  const activeRect = activeLink.getBoundingClientRect()

  // 仅在 active 链接超出容器可视区域时才滚动
  if (
    activeRect.top < containerRect.top ||
    activeRect.bottom > containerRect.bottom
  ) {
    // 计算目标 scrollTop：让 active 链接居中显示
    const relativeTop = activeLink.offsetTop - container.offsetTop
    const target = relativeTop - containerRect.height / 2 + activeRect.height / 2

    container.scrollTo({
      top: target,
      behavior: 'smooth',
    })
  }
}, 100) // ★ 与 VitePress 内部 useActiveAnchor 的节流频率一致

onMounted(() => {
  window.addEventListener('scroll', scrollToActiveOutline, { passive: true })
  // 首次激活
  setTimeout(scrollToActiveOutline, 200)
})

onUnmounted(() => {
  window.removeEventListener('scroll', scrollToActiveOutline)
})
</script>

<template>
  <span style="display: none" />
</template>