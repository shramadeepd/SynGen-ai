<template>
  <form @submit.prevent="handleSubmit" class="flex space-x-2">
    <input
      type="text"
      v-model="message"
      placeholder="Ask something about your business..."
      class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      :disabled="isLoading"
    />
    <button
      type="submit"
      :disabled="!message.trim() || isLoading"
      class="bg-blue-600 text-white rounded-lg p-2 hover:bg-blue-700 transition-colors"
      :class="{'opacity-50 cursor-not-allowed': !message.trim() || isLoading}"
    >
      <Send size="20" />
    </button>
  </form>
</template>

<script>
import { ref } from 'vue';
import { Send } from 'lucide-vue-next'; // Update the import path if necessary

export default {
  props: {
    onSendMessage: {
      type: Function,
      required: true,
    },
    isLoading: {
      type: Boolean,
      required: true,
    },
  },
  setup(props) {
    const message = ref("");

    const handleSubmit = () => {
      if (message.value.trim() && !props.isLoading) {
        props.onSendMessage(message.value);
        message.value = "";
      }
    };

    return {
      message,
      handleSubmit,
    };
  },
};
</script>