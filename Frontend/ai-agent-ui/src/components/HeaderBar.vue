<template>
  <div class="bg-white border-b border-gray-200 py-6 px-4 flex items-center">
    <div class="bg-blue-500 p-2 rounded-full mr-3">
      <Bot :size="24" class="text-white" />
    </div>
    <div>
      <h1 class="font-bold text-xl">BusinessAI</h1>
      <p class="text-gray-500 text-sm">Your intelligent business assistant</p>
    </div>
  </div>
</template>

<script>
import { Bot } from 'lucide-vue-next'

export default {
  name: 'ChatHeader',
  components: {
    Bot
  }
}
</script>
