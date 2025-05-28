<template>
  <div class="flex space-x-1">
    <div class="w-2 h-2 rounded-full animate-pulse bg-current"></div>
    <div class="w-2 h-2 rounded-full animate-pulse delay-150 bg-current"></div>
    <div class="w-2 h-2 rounded-full animate-pulse delay-300 bg-current"></div>
  </div>
</template>

<script>
export default {
  name: 'LoadingDots'
}
</script>
<style scoped>
.dots {
  display: flex;
  gap: 6px;
  padding: 1rem;
}

.dot {
  width: 8px;
  height: 8px;
  background: #888;
  border-radius: 50%;
  animation: blink 1.4s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 80%, 100% {
    opacity: 0;
  }
  40% {
    opacity: 1;
  }
}

</style>