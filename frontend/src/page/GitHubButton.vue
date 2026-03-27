<template>
  <a
    :href="href"
    target="_blank"
    rel="noopener noreferrer"
    class="github-btn"
    @mouseenter="hovered = true"
    @mouseleave="hovered = false"
  >
    <span class="github-btn__track" :class="{ 'github-btn__track--hovered': hovered }" />

    <span class="github-btn__content">
      <svg
        class="github-btn__icon"
        :class="{ 'github-btn__icon--spin': hovered }"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        fill="currentColor"
      >
        <path
          d="M12 0C5.37 0 0 5.373 0 12c0 5.303 3.438 9.8 8.205 11.387.6.113.82-.258.82-.577
             0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.757-1.333-1.757
             -1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304
             3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931
             0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322
             3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404
             2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84
             1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823
             2.222 0 1.606-.015 2.896-.015 3.286 0 .322.216.694.825.576C20.565 21.795
             24 17.298 24 12c0-6.627-5.373-12-12-12z"
        />
      </svg>

      <span class="github-btn__label">Sprawdź repozytorium na GitHub</span>

      <svg
        class="github-btn__arrow"
        :class="{ 'github-btn__arrow--move': hovered }"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          d="M3 8h10M9 4l4 4-4 4"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </span>
  </a>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  href: {
    type: String,
    default: 'https://github.com',
  },
})

const hovered = ref(false)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700&display=swap');

.github-btn {
  --gh-bg: #0d0f1e;
  --gh-fg: #39ff6e;
  --gh-accent: #ff2d78;
  --gh-border: #ff2d78;
  --gh-glow-pink: rgba(255, 45, 120, 0.6);
  --gh-glow-green: rgba(57, 255, 110, 0.4);

  position: relative;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--gh-fg);
  background: var(--gh-bg);
  border: 1px solid var(--gh-border);
  border-radius: 6px;
  padding: 7px 13px;
  overflow: hidden;
  box-shadow:
    0 0 8px var(--gh-glow-pink),
    inset 0 0 8px rgba(255, 45, 120, 0.08);
  transition:
    box-shadow 0.3s ease,
    color 0.3s ease;
  cursor: pointer;
}

.github-btn:hover {
  color: #fff;
  box-shadow:
    0 0 14px var(--gh-glow-pink),
    0 0 28px var(--gh-glow-pink),
    inset 0 0 12px rgba(255, 45, 120, 0.15);
}

/* Animated shimmer track */
.github-btn__track {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    transparent 40%,
    rgba(255, 45, 120, 0.15) 50%,
    transparent 60%
  );
  background-size: 200% 100%;
  background-position: 150% 0;
  transition: background-position 0s;
  pointer-events: none;
}

.github-btn__track--hovered {
  background-position: -50% 0;
  transition: background-position 0.55s ease;
}

/* Content row */
.github-btn__content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 7px;
  z-index: 1;
}

/* GitHub logo */
.github-btn__icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.github-btn__icon--spin {
  transform: rotate(360deg);
}

/* Label */
.github-btn__label {
  letter-spacing: 0.01em;
  white-space: nowrap;
}

/* Arrow */
.github-btn__arrow {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: var(--gh-accent);
  transition: transform 0.25s ease;
  transform: translateX(4px);
}
</style>