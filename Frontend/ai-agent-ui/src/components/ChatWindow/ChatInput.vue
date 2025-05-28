<template>
  <div class="input-wrapper">
    <form @submit.prevent="handleSubmit" class="flex items-center space-x-2 w-full max-w-2xl">
      <input
        type="text"
        v-model="message"
        placeholder="Ask something about your business..."
        class="w-full text-xl border border-gray-300 rounded-xl px-8 py-5 text-black bg-white min-h-[64px"
        :disabled="isLoading"
      />
      <button
        type="submit"
        :disabled="!message.trim() || isLoading"
        class="bg-blue-500 text-white px-4 py-2 rounded-md"
      >
        <Send size="24" />
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { Send } from 'lucide-vue-next';

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

<style scoped>
.input-wrapper {
  display: flex;
  padding: 1rem;
  background-color: transparent; /* For testing visibility - adjust as needed */
  border-top: 1px solid #333;
  align-items: center;
  justify-content: center;
}

input {
  flex: 1;
  padding: 1rem 1rem;         /* Increased padding */
  font-size: 1rem;           /* Increased font size */
  border-radius: 16px;          /* More rounded */
  border: 2px solid #333;
  min-height: 40px;             /* Taller box */
  width: 120%;
  outline: none;
  transition: all 0.3s ease;
}


input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.4);
}
</style>