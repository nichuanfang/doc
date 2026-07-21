<script setup lang="ts">
import { useRoute } from 'vitepress'
import { onMounted, onUnmounted, watch } from 'vue'

const route = useRoute()
let ticking = false
let scrollHandler: (() => void) | null = null

function scrollActiveLink() {
  requestAnimationFrame(() => {
    const activeLink = document.querySelector<HTMLElement>(
      '.VPDocAsideOutline .outline-link.active',
    )
    if (!activeLink) return

    activeLink.scrollIntoView({
      block: 'center',
      behavior: 'smooth',
    })
  })
}

function handleScroll() {
  if (!ticking) {
    ticking = true
    requestAnimationFrame(() => {
      scrollActiveLink()
      ticking = false
    })
  }
}

// 路由变化时触发
watch(() => route.path, scrollActiveLink, { immediate: true })

onMounted(() => {
  scrollHandler = handleScroll
  window.addEventListener('scroll', scrollHandler, { passive: true })
})

onUnmounted(() => {
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler)
  }
})
</script>

<template>
  <!-- 该组件仅负责滚动逻辑，不渲染任何内容 -->
</template>