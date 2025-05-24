import { ref, onMounted, watch } from 'vue'
import ChatHeader from '../components/ChatHeader.vue'
import ChatInput from '../components/ChatWindow/ChatInput.vue'
import ChatMessage from '../components/ChatWindow/ChatMessage.vue'
import { useChat } from '../hooks/useChat'

const Index = {
  components: {
    ChatHeader,
    ChatInput,
    ChatMessage
  },
  setup() {
    const { messages, isLoading, sendMessage } = useChat()
    const messagesEndRef = ref(null)

    // Scroll to bottom whenever messages change
    onMounted(() => {
      watch(messages, () => {
        messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
      })
    })

    return {
      messages,
      isLoading,
      sendMessage,
      messagesEndRef
    }
  },
  template: `
    <div class="flex flex-col h-screen ">
      <ChatHeader />
      
      <!-- Chat messages area -->
      <div class="flex-1 overflow-y-auto ">
        <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center space-y-4">
            <h2 class="text-2xl font-semibold text-gray-700">Welcome to BusinessAI</h2>
            <p class="text-gray-500 max-w-md">Your AI assistant for business insights and answers. Ask me anything about your business needs!</p>
          </div>
        </div>
        <template v-else>
          <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :message="message.content"
            :isUser="message.isUser"
            :timestamp="message.timestamp"
          />
        </template>
        <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :message="message.content"
            :isUser="message.isUser"
            :timestamp="message.timestamp"
            :isLoading="false"
          />

        <div ref="messagesEndRef" />
      </div>
      
      <!-- Input area -->
      <div class="border-t border-gray-300 p-4 bg-white">
        <ChatInput :onSendMessage="sendMessage" :isLoading="isLoading" />
      </div>
    </div>
  `
}

export default Index