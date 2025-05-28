<template>
  <div class="chat-history">
    <h2 class="title">Chat History</h2>
    <ul>
      <li 
        v-for="(chat, idx) in chats" 
        :key="chat.id"
        :class="{ active: idx === selectedChatIndex }"
        @click="selectChat(idx)"
      >
        {{ chat.title || `Chat ${idx + 1}` }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Dummy data for now
const chats = ref([
  { id: 1, title: 'Order Inquiry' },
  { id: 2, title: 'Support Request' },
  { id: 3, title: 'General Question' }
])
const selectedChatIndex = ref(0)

function selectChat(idx) {
  selectedChatIndex.value = idx
  // TODO: emit event or call composable to load selected chat
}
</script>

<style scoped>
.chat-history {
  width: 280px;
  /* background: rgba(30, 41, 59, 0.95);
   */
  background: transparent;
  color: #140575;
  padding: 1rem;
  border-right: 1px solid #38064f;
  height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.title {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  font-weight: bold;
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}
li {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 0.25rem;
  transition: background 0.2s;
}
li.active, li:hover {
  background: #f1f1f0;
  display: flex;
}
</style>