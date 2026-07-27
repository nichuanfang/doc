<script setup lang="ts">
import { onMounted, onUnmounted, nextTick } from 'vue'

// ===== 可调常量 =====
/** 用户交互后锁定自动滚动的时长(ms) */
const INTERACTION_LOCK_MS = 1500
/** scrollend 不可用时的兜底超时(ms) */
const SCROLLEND_FALLBACK_MS = 400
/** 判定"已在可视区域内"的滚动阈值(px) */
const SCROLL_THRESHOLD_PX = 8

let asideEl: HTMLElement | null = null
let observer: MutationObserver | null = null
// 统一管理本组件添加的所有事件监听器,unmount 时一键清理
let abortController: AbortController | null = null

let userInteracting = false
let interactionTimer: ReturnType<typeof setTimeout> | null = null

let autoScrollingTimer: ReturnType<typeof setTimeout> | null = null
/** 上一次滚动动画的 scrollend 监听器移除函数,防止多次触发时监听器堆叠 */
let removePrevScrollEndListener: (() => void) | null = null

// ===== 辅助函数 =====

/** 标记用户正在与 outline 交互,暂时关闭自动滚动 */
function markUserInteraction() {

  userInteracting = true
  if (interactionTimer) clearTimeout(interactionTimer)
  interactionTimer = setTimeout(() => {
    userInteracting = false
    // 解锁后主动补一次纠正,防止交互窗口内的 active 变化被吞掉
    requestAnimationFrame(scrollActiveIntoView)
  }, INTERACTION_LOCK_MS)
}

/** 判断当前 active 项是否为大纲中的最后一项 */
function isLastOutlineLink(el: HTMLElement, container: HTMLElement): boolean {
  const allLinks = container.querySelectorAll('.outline-link')
  return allLinks.length > 0 && el === allLinks[allLinks.length - 1]
}

/** 将当前 active 的 outline 项滚入可视区域 */
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
  const maxScroll = Math.max(0, container.scrollHeight - containerHeight)

  // 计算目标滚动位置:尽量居中
  let target = relativeTop - containerHeight / 2 + activeHeight / 2

  // 特殊处理:如果 active 是最后一项,直接贴底,避免底部留空白
  if (isLastOutlineLink(active, container)) {
    target = maxScroll
  }

  // 边界钳制,确保首项可到顶端、末项可到底端
  target = Math.max(0, Math.min(target, maxScroll))

  // 已在可视区域内则跳过
  if (Math.abs(container.scrollTop - target) < SCROLL_THRESHOLD_PX) return

  // 避免上一次滚动的 scrollend 监听器堆叠
  removePrevScrollEndListener?.()

  if (autoScrollingTimer) clearTimeout(autoScrollingTimer)

  const onScrollEnd = () => {
    container.removeEventListener('scrollend', onScrollEnd)
    removePrevScrollEndListener = null
    if (autoScrollingTimer) clearTimeout(autoScrollingTimer)
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
  requestAnimationFrame(scrollActiveIntoView)
}

const onPageShow = (e: PageTransitionEvent) => {
  if (e.persisted) restore()
}

/** outline-link.active 变化的防抖处理 */
function onActiveChanged() {
  requestAnimationFrame(scrollActiveIntoView)
}

// ===== 生命周期 =====

onMounted(() => {
  nextTick(() => {
    asideEl = document.querySelector('.aside-container') as HTMLElement | null
    if (!asideEl) return

    abortController = new AbortController()
    const { signal } = abortController

    // 监听用户手动操作事件,去掉 scroll,避免自动滚动产生的误判
    // wheel → 滚轮, touchstart → 触屏滑动
    // mousedown / pointerdown → 拖动滚动条(修复之前遗漏的交互方式)
    ;['wheel', 'touchstart', 'mousedown', 'pointerdown'].forEach((evt) => {
      asideEl!.addEventListener(evt, markUserInteraction, { passive: true, signal })
    })

    // 监听 active 类变化
    // 依赖 VitePress 默认主题内部结构:
    //   .aside-container / .outline-link / .active
    // VitePress useActiveAnchor 通过 throttleAndDebounce(100ms) 控制 class 切换频率,
    // 此处 MutationObserver 配合防抖进一步优化快速滚动时的体验。
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

    // bfcache(前进/后退)恢复
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
  removePrevScrollEndListener?.()
  removePrevScrollEndListener = null

  asideEl = null
})
</script>

<template>
  <!-- 仅用于挂载逻辑,不渲染可见内容 -->
  <span style="display: none" aria-hidden="true" />
</template>