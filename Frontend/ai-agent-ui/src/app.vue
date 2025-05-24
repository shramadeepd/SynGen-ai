<template>
  <div id="app">
    <HeaderBar />

    <div class="main-layout">
      <!-- Sidebar: ChatHistory -->
      <ChatHistory />

      <!-- Main Chat Content -->
      <div class="chat-content">
        <!-- Messages container -->
        <div class="messages-container">
          <div v-if="messages.length === 0" class="empty-state">
            <p>Start a conversation with BusinessAI</p>
          </div>
          <div v-else>
            <ChatMessage
              v-for="(msg, idx) in messages"
              :key="idx"
              :message="msg.content"
              :isUser="msg.isUser"
              :timestamp="msg.timestamp"
            />
          </div>
        </div>
        <!-- Chat Input at the bottom -->
        <div class=""chat-input>
        <ChatInput
          :onSendMessage="sendMessage"
          :isLoading="isLoading"
        />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useChat } from './hooks/Usehooks.js'
import HeaderBar from './components/HeaderBar.vue'
import ChatInput from './components/ChatWindow/ChatInput.vue'
import ChatMessage from './components/ChatWindow/ChatMessage.vue'
import ChatHistory from './components/ChatWindow/ChatHistory.vue'

const { messages, isLoading, sendMessage } = useChat()
</script>

<style scoped>
/* Base app styles */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  /* box-sizing: border-box; */
}

/* Layout: side-by-side sidebar and main chat content */
.main-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

/* Sidebar styling is handled in ChatHistory */
 
/* Chat content (messages and input) */
.chat-content {
  height: 80%;
  flex: 1;
  display: flex;
  flex-direction: column;
  /* background: rgba(30, 41, 59, 0.7); */
  background: transparent;
  color: #fff;
}

/* Make messages container scrollable */
.messages-container {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

/* Centered empty state message */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 1.2rem;
  color: #ddd;
}

.chat-input {
  border-top: 1px solid #ccc;
  padding: 1rem;
  background-color: #fff;
}
</style>