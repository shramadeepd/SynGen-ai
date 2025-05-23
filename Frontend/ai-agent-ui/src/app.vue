<!-- <template>
  <div id="app">
    <HeaderBar />
    <ChatInput />
    <ChatMessage />
    <LoadingDots />
    <h1>Hello from Vue!</h1>
  </div>
</template>

<script setup>
// Add any logic or imports here
import HeaderBar from './components/HeaderBar.vue'
import ChatInput from './components/ChatWindow/ChatInput.vue'
import ChatMessage from './components/ChatWindow/ChatMessage.vue'
import LoadingDots from './components/ChatWindow/LoadingDots.vue'
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  padding: 2rem;
}
</style> -->

<template>
  <div id="app">
    <HeaderBar />
    <div class="chat-container">
      <div v-if="messages.length === 0" class="empty-state">
        <p>Start a conversation with BusinessAI</p>
      </div>
      <div v-else class="messages-container">
        <ChatMessage 
          v-for="(msg, index) in messages" 
          :key="index"
          :message="msg.content"
          :isUser="msg.isUser"
          :timestamp="msg.timestamp"
        />
      </div>
      <div v-if="isLoading" class="loading-container">
        <ChatMessage 
          message=""
          :isUser="false"
          :isLoading="true"
          :timestamp="new Date()"
        />
      </div>
    </div>
    <ChatInput 
      :onSendMessage="sendMessage"
      :isLoading="isLoading"
    />
  </div>
</template>

<script setup>
import { useChat } from './hooks/Usehooks.js'
import HeaderBar from './components/HeaderBar.vue'
import ChatInput from './components/ChatWindow/ChatInput.vue'
import ChatMessage from './components/ChatWindow/ChatMessage.vue'
import LoadingDots from './components/ChatWindow/LoadingDots.vue'

const { messages, isLoading, sendMessage } = useChat()
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.loading-container {
  margin-top: 1rem;
}
</style>
