<script setup>
defineProps({ size: { type: Number, default: 56 } })
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 48 48" fill="none">
    <defs>
      <linearGradient id="bondlyHeart" x1="0" y1="0" x2="48" y2="48">
        <stop offset="0" stop-color="#7c4dff" />
        <stop offset="0.5" stop-color="#b552f5" />
        <stop offset="1" stop-color="#ff7a59" />
      </linearGradient>
    </defs>
    <path
      d="M24 42S6 30.5 6 18.5C6 12.7 10.7 8 16.5 8c3.4 0 6.6 1.7 8.5 4.3C26.9 9.7 30.1 8 33.5 8 39.3 8 44 12.7 44 18.5 44 30.5 24 42 24 42Z"
      transform="translate(-1 -1)"
      fill="url(#bondlyHeart)"
    />
  </svg>
</template>
