<script setup lang="ts">
import { onMounted, onUnmounted, nextTick } from 'vue'

// ===== 可调常量 =====
/** 用户交互后锁定自动滚动的时长(ms) */
const INTERACTION_LOCK_MS = 1500
/** 页面刷新/恢复后延迟触发定位的时长(ms) */
const RESTORE_DELAY_MS = 120
/** scrollend 不可用时的兜底超时(ms) */
const SCROLLEND_FALLBACK_MS = 1500
/** 判定"已在可视区域内"的滚动阈值(px) */
const SCROLL_THRESHOLD_PX = 8
/** MutationObserver 防抖间隔(ms)，防止快速滚动时 smooth 动画堆叠 */
const OBSERVER_DEBOUNCE_MS = 60

let asideEl: HTMLElement | null = null
let observer: MutationObserver | null = null
// 统一管理本组件添加的所有事件监听器,unmount 时一键清理
let abortController: AbortController | null = null

let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null

/** 由代码自身触发滚动时置位,避免把自动滚动误判为用户交互 */
let isAutoScrolling = false
let autoScrollingTimer: ReturnType<typeof setTimeout> | null = null
/** 上一次滚动动画的 scrollend 监听器移除函数,防止多次触发时监听器堆叠 */
let removePrevScrollEndListener: (() => void) | null = null

/** MutationObserver 防抖定时器 */
let observerDebounceTimer: ReturnType<typeof setTimeout> | null = null

/** 标记用户正在与 outline 交互,暂时关闭自动滚动 */
function markUserInteraction() {
  if (isAutoScrolling) return

  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  interactionTimer = setTimeout(() => {
    userInteracting = false
    // 解锁后主动补一次纠正,防止交互窗口内的 active 变化被吞掉
    requestAnimationFrame(scrollActiveIntoView)
  }, INTERACTION_LOCK_MS)
}

/** 将当前 active 的 outline 项滚入可视区域(居中 + 边界钳制,保证可到达顶端/底端) */
function scrollActiveIntoView() {
  if (userInteracting || !asideEl) return

  const active = asideEl.querySelector('.outline-link.active') as HTMLElement | null
  if (!active) return

  const container = asideEl
  const cRect = container.getBoundingClientRect()
  const aRect = active.getBoundingClientRect()
  const relativeTop = aRect.top - cRect.top + container.scrollTop
  const activeHeight = aRect.height
  const containerHeight = container.clientHeight
  const maxScroll = container.scrollHeight - containerHeight

  // 目标:尽量居中,但钳制在 [0, maxScroll],确保首项可到顶端、末项可到底端
  let target = relativeTop - containerHeight / 2 + activeHeight / 2
  target = Math.max(0, Math.min(target, maxScroll))

  // 已在可视区域内则跳过
  if (Math.abs(container.scrollTop - target) < SCROLL_THRESHOLD_PX) return

  // 避免上一次滚动的 scrollend 监听器堆叠
  removePrevScrollEndListener?.()

  isAutoScrolling = true
  if (autoScrollingTimer) clearTimeout(autoScrollingTimer)

  const onScrollEnd = () => {
    isAutoScrolling = false
    container.removeEventListener('scrollend', onScrollEnd)
    removePrevScrollEndListener = null
  }
  removePrevScrollEndListener = () => container.removeEventListener('scrollend', onScrollEnd)

  container.addEventListener('scrollend', onScrollEnd, { once: true })
  // 兜底:不支持 scrollend 的浏览器用超时
  autoScrollingTimer = setTimeout(onScrollEnd, SCROLLEND_FALLBACK_MS)

  container.scrollTo({
    top: target,
    behavior: 'smooth'
  })
}

/** 延迟兜底,用于刷新 / 滚动恢复 / bfcache 场景 */
function restore() {
  setTimeout(() => {
    requestAnimationFrame(scrollActiveIntoView)
  }, RESTORE_DELAY_MS)
}

const onPageShow = (e: PageTransitionEvent) => {
  if (e.persisted) restore()
}

/** outline-link.active 变化的防抖处理 */
function onActiveChanged() {
  if (observerDebounceTimer) clearTimeout(observerDebounceTimer)
  observerDebounceTimer = setTimeout(() => {
    requestAnimationFrame(scrollActiveIntoView)
  }, OBSERVER_DEBOUNCE_MS)
}

onMounted(() => {
  nextTick(() => {
    asideEl = document.querySelector('.aside-container') as HTMLElement | null
    if (!asideEl) return

    abortController = new AbortController()
    const { signal } = abortController

    // 只监听真正代表用户手动操作的事件,去掉 scroll,避免自动滚动产生的误判
    // wheel -> 滚轮操作, touchstart -> 触屏操作
    // mousedown / pointerdown -> 拖动滚动条操作（覆盖前两者遗漏的手动交互）
    ;['wheel', 'touchstart', 'mousedown', 'pointerdown'].forEach((evt) => {
      asideEl!.addEventListener(evt, markUserInteraction, { passive: true, signal })
    })

    // 监听 active 类变化(依赖 VitePress 默认主题内部结构:
    // .aside-container / .outline-link / .active,升级 VitePress 时需重新核对)
    observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        const target = m.target as HTMLElement
        if (
          m.type === 'attributes' &&
          m.attributeName === 'class' &&
          target.classList.contains('outline-link') &&
          target.classList.contains('active')
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

    // 初次定位
    restore()

    // 浏览器滚动恢复后通常会触发一次 scroll,再补一次
    window.addEventListener('scroll', () => restore(), { once: true, passive: true, signal })

    // bfcache(前进 / 后退)恢复
    window.addEventListener('pageshow', onPageShow, { signal })
  })
})

onUnmounted(() => {
  observer?.disconnect()
  observer = null

  // 一次性移除本组件添加的所有事件监听器
  abortController?.abort()
  abortController = null

  if (interactionTimer) clearTimeout(interactionTimer)
  if (autoScrollingTimer) clearTimeout(autoScrollingTimer)
  if (observerDebounceTimer) clearTimeout(observerDebounceTimer)
  removePrevScrollEndListener?.()
  removePrevScrollEndListener = null

  asideEl = null
})
</script>

<template>
  <!-- 仅用于挂载逻辑,不渲染可见内容 -->
  <span style="display: none" aria-hidden="true" />
</template>