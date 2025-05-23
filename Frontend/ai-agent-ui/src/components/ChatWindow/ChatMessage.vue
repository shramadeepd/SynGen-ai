<template>
  <div :class="`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`">
    <div
      :class="`flex max-w-[80%] md:max-w-[70%] rounded-lg p-4 ${
        isUser ? 'bg-gray-100 text-gray-800' : 'bg-blue-600 text-white'
      }`"
    >
      <div :class="`flex-shrink-0 ${isUser ? 'order-last ml-2' : 'mr-2'}`">
        <div :class="`${isUser ? 'bg-gray-200' : 'bg-blue-500'} p-1 rounded-full`">
          <component :is="isUser ? 'User' : 'Bot'" size="16" :class="`${isUser ? 'text-gray-600' : 'text-white'}`" />
        </div>
      </div>
      <div class="space-y-2">
        <LoadingDots v-if="isLoading" />
        <template v-else>
          <div class="whitespace-pre-wrap">{{ message }}</div>
          <div :class="`text-xs opacity-70 ${isUser ? 'text-gray-500' : 'text-blue-100'}`">
            {{ formatTimestamp(timestamp) }}
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { format } from 'date-fns'
import { Bot, User } from 'lucide-vue-next'
import LoadingDots from './LoadingDots.vue'

export default {
  components: {
    Bot,
    User,
    LoadingDots
  },
  props: {
    message: {
      type: String,
      required: true
    },
    isUser: {
      type: Boolean,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    timestamp: {
      type: Date,
      required: true
    }
  },
  methods: {
    formatTimestamp(timestamp) {
      return format(timestamp, 'HH:mm')
    }
  }
}
</script>