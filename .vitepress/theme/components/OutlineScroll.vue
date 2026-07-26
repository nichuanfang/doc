<script setup lang="ts">
import { onMounted, onUnmounted, nextTick } from 'vue'

let observer: MutationObserver | null = null
let asideEl: HTMLElement | null = null
let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null

function markUserInteraction() {
  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  // resume auto-scroll shortly after the user stops interacting
  interactionTimer = setTimeout(() => {
    userInteracting = false
  }, 1500)
}

function scrollActiveIntoView() {
  if (userInteracting || !asideEl) return

  const active = asideEl.querySelector('.outline-link.active') as HTMLElement | null
  if (!active) return

  // Prefer the nearest scrollable ancestor (the official .aside-container)
  active.scrollIntoView({
    behavior: 'smooth',
    block: 'nearest',   // never jumps the page; only moves the outline
    inline: 'nearest'
  })
}

onMounted(() => {
  // wait one frame so the default outline has rendered
  nextTick(() => {
    asideEl = document.querySelector('.aside-container') as HTMLElement | null
    if (!asideEl) return

    // listen for user interaction on the outline
    ;['wheel', 'touchstart', 'pointerdown', 'mouseenter'].forEach(evt => {
      asideEl!.addEventListener(evt, markUserInteraction, { passive: true })
    })

    // observe class changes on any outline link
    observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (
          m.type === 'attributes' &&
          m.attributeName === 'class' &&
          (m.target as HTMLElement).classList.contains('active')
        ) {
          // small delay so the marker animation has started
          requestAnimationFrame(() => scrollActiveIntoView())
          break
        }
      }
    })

    observer.observe(asideEl, {
      attributes: true,
      attributeFilter: ['class'],
      subtree: true
    })

    // initial positioning (e.g. deep-link / page restore)
    requestAnimationFrame(scrollActiveIntoView)
  })
})

onUnmounted(() => {
  observer?.disconnect()
  if (interactionTimer) clearTimeout(interactionTimer)
  if (asideEl) {
    ;['wheel', 'touchstart', 'pointerdown', 'mouseenter'].forEach(evt => {
      asideEl!.removeEventListener(evt, markUserInteraction)
    })
  }
})
</script>

<template>
  <!-- invisible helper – the slot is only used for mounting -->
  <span style="display: none" aria-hidden="true" />
</template>