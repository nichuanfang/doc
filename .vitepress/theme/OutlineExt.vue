<!-- .vitepress/theme/OutlineExt.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { routeChangeSignal } from './routeSignal'

let lastActiveHref = ''
let userInteracting = false
let interactTimer: ReturnType<typeof setTimeout> | null = null
let observer: MutationObserver | null = null
let containerEl: HTMLElement | null = null

// ==================== 核心功能函数 ====================

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

function pauseAutoScroll() {
    userInteracting = true
    if (interactTimer) clearTimeout(interactTimer)
    interactTimer = setTimeout(() => {
        userInteracting = false
    }, 1200)
}

function setupContainerListeners(container: HTMLElement) {
    if (container === containerEl) return

    if (containerEl) {
        containerEl.removeEventListener('wheel', pauseAutoScroll)
        containerEl.removeEventListener('touchstart', pauseAutoScroll)
        containerEl.removeEventListener('touchmove', pauseAutoScroll)
    }

    containerEl = container
    container.addEventListener('wheel', pauseAutoScroll, { passive: true })
    container.addEventListener('touchstart', pauseAutoScroll, { passive: true })
    container.addEventListener('touchmove', pauseAutoScroll, { passive: true })
}

function checkAndScroll() {
    const container = document.querySelector<HTMLElement>('.aside-container')
    const activeLink = document.querySelector<HTMLAnchorElement>(
        '.VPDocAsideOutline .outline-link.active'
    )

    if (container) setupContainerListeners(container)

    const currentHref = activeLink?.getAttribute('href') || ''

    if (currentHref && currentHref !== lastActiveHref && !userInteracting) {
        lastActiveHref = currentHref
        doScroll(container, activeLink)
    } else if (!currentHref) {
        lastActiveHref = ''
    }
}

// 监听路由变化
watch(routeChangeSignal, () => {
    lastActiveHref = ''
    userInteracting = false
    setTimeout(checkAndScroll, 60)
})

function setupObserver() {
    if (observer) observer.disconnect()

    observer = new MutationObserver(checkAndScroll)
    observer.observe(document.body, {
        attributes: true,
        subtree: true,
        attributeFilter: ['class'],
    })
}

// ==================== 生命周期 ====================

onMounted(() => {
    setupObserver()
    setTimeout(checkAndScroll, 100)
})

onUnmounted(() => {
    if (observer) {
        observer.disconnect()
        observer = null
    }
    if (interactTimer) {
        clearTimeout(interactTimer)
        interactTimer = null
    }
    if (containerEl) {
        containerEl.removeEventListener('wheel', pauseAutoScroll)
        containerEl.removeEventListener('touchstart', pauseAutoScroll)
        containerEl.removeEventListener('touchmove', pauseAutoScroll)
        containerEl = null
    }
})
</script>

<template>
    <span style="display: none" />
</template>