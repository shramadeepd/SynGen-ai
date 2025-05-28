<template>
  <div class="flex h-full">
    <!-- Chat history sidebar -->
    <div class="w-80 bg-white border-r border-gray-200 flex flex-col">
      <div class="p-4 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Chat History</h3>
        <button
          @click="clearHistory"
          class="mt-2 text-sm text-red-600 hover:text-red-700"
        >
          Clear History
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div v-if="apiStore.queryHistory.length === 0" class="text-center py-8">
          <ChatBubbleLeftRightIcon class="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p class="text-sm text-gray-500">No conversations yet</p>
        </div>
        
        <div
          v-for="query in apiStore.queryHistory"
          :key="query.id"
          @click="loadQuery(query)"
          class="p-3 rounded-lg border cursor-pointer hover:bg-gray-50 transition-colors"
          :class="{ 'bg-blue-50 border-blue-200': selectedQuery?.id === query.id }"
        >
          <p class="text-sm font-medium text-gray-900 truncate">{{ query.question }}</p>
          <div class="flex items-center justify-between mt-1">
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" :class="getQueryTypeBadge(query.type)">
              {{ query.type }}
            </span>
            <span class="text-xs text-gray-500">{{ formatDate(query.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main chat area -->
    <div class="flex-1 flex flex-col">
      <!-- Messages area -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6" ref="messagesContainer">
        <!-- Welcome message -->
        <div v-if="messages.length === 0" class="text-center py-12">
          <div class="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <ChatBubbleLeftRightIcon class="h-8 w-8 text-blue-600" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Welcome to SynGen AI</h3>
          <p class="text-gray-600 mb-6">Ask questions about your supply chain data or search policy documents.</p>
          
          <!-- Quick start buttons -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
            <button
              v-for="sample in quickStartQueries"
              :key="sample.question"
              @click="sendMessage(sample.question)"
              class="p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div class="flex items-start">
                <component :is="sample.icon" class="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ sample.question }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ sample.description }}</p>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Chat messages -->
        <div v-for="message in messages" :key="message.id" class="space-y-4">
          <!-- User message -->
          <div class="flex justify-end">
            <div class="max-w-3xl bg-blue-600 text-white rounded-lg px-4 py-2">
              <p class="text-sm">{{ message.question }}</p>
              <p class="text-xs text-blue-100 mt-1">{{ formatDate(message.timestamp) }}</p>
            </div>
          </div>

          <!-- AI response -->
          <div class="flex justify-start">
            <div class="max-w-4xl bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
              <!-- Response type indicator -->
              <div class="flex items-center mb-3">
                <div class="w-2 h-2 rounded-full mr-2" :class="getQueryTypeColor(message.type)"></div>
                <span class="text-xs font-medium text-gray-600 uppercase tracking-wide">{{ message.type }} Response</span>
              </div>

              <!-- SQL Query Response -->
              <div v-if="message.type === 'sql' && message.result.sql">
                <div class="mb-4">
                  <h4 class="text-sm font-semibold text-gray-900 mb-2">Generated SQL:</h4>
                  <div class="bg-gray-900 text-green-400 p-3 rounded-md text-sm font-mono overflow-x-auto">
                    {{ message.result.sql }}
                  </div>
                </div>

                <div v-if="message.result.rows && message.result.rows.length > 0" class="mb-4">
                  <h4 class="text-sm font-semibold text-gray-900 mb-2">Results ({{ message.result.rows.length }} rows):</h4>
                  <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-md">
                      <thead class="bg-gray-50">
                        <tr>
                          <th
                            v-for="(value, key) in message.result.rows[0]"
                            :key="key"
                            class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {{ key }}
                          </th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="(row, index) in message.result.rows.slice(0, 10)" :key="index">
                          <td
                            v-for="(value, key) in row"
                            :key="key"
                            class="px-3 py-2 whitespace-nowrap text-sm text-gray-900"
                          >
                            {{ formatValue(value) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="message.result.rows.length > 10" class="text-xs text-gray-500 mt-2 text-center">
                      Showing first 10 of {{ message.result.rows.length }} results
                    </div>
                  </div>
                </div>

                <div v-if="message.result.explanation" class="mb-4">
                  <h4 class="text-sm font-semibold text-gray-900 mb-2">Explanation:</h4>
                  <p class="text-sm text-gray-700">{{ message.result.explanation }}</p>
                </div>
              </div>

              <!-- Document/RAG Response -->
              <div v-else-if="message.type === 'policy_query' || message.type === 'document'">
                <div v-if="message.result.answer" class="mb-4">
                  <h4 class="text-sm font-semibold text-gray-900 mb-2">Answer:</h4>
                  <p class="text-sm text-gray-700">{{ message.result.answer }}</p>
                </div>

                <div v-if="message.result.sources && message.result.sources.length > 0" class="mb-4">
                  <h4 class="text-sm font-semibold text-gray-900 mb-2">Sources:</h4>
                  <div class="space-y-2">
                    <div
                      v-for="(source, index) in message.result.sources"
                      :key="index"
                      class="p-3 bg-gray-50 rounded-md"
                    >
                      <p class="text-sm text-gray-700">{{ source.text || source }}</p>
                      <div v-if="source.metadata" class="mt-1">
                        <span class="text-xs text-gray-500">
                          Source: {{ source.metadata.source || 'Document' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Generic response -->
              <div v-else>
                <p class="text-sm text-gray-700">{{ message.result.explanation || message.result.answer || 'Response received' }}</p>
              </div>

              <!-- Error handling -->
              <div v-if="message.error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p class="text-sm text-red-700">{{ message.error }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="apiStore.isLoading" class="flex justify-start">
          <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div class="flex items-center space-x-2">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span class="text-sm text-gray-600">Processing your query...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="border-t border-gray-200 p-4">
        <form @submit.prevent="handleSubmit" class="flex space-x-4">
          <div class="flex-1">
            <input
              v-model="inputMessage"
              type="text"
              placeholder="Ask a question about your data or search documents..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="apiStore.isLoading"
            />
          </div>
          <button
            type="submit"
            :disabled="!inputMessage.trim() || apiStore.isLoading"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon class="h-5 w-5" />
          </button>
        </form>
        
        <!-- Query type selector -->
        <div class="mt-3 flex items-center space-x-4">
          <span class="text-sm text-gray-600">Query type:</span>
          <label class="flex items-center">
            <input
              v-model="queryType"
              type="radio"
              value="auto"
              class="mr-2"
            />
            <span class="text-sm text-gray-700">Auto-detect</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="queryType"
              type="radio"
              value="sql"
              class="mr-2"
            />
            <span class="text-sm text-gray-700">SQL Query</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="queryType"
              type="radio"
              value="document"
              class="mr-2"
            />
            <span class="text-sm text-gray-700">Document Search</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useApiStore } from '../stores/api'
import { format } from 'date-fns'
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  ChartBarIcon,
  DocumentTextIcon,
  UsersIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const apiStore = useApiStore()

const inputMessage = ref('')
const queryType = ref('auto')
const selectedQuery = ref(null)
const messagesContainer = ref(null)

// Quick start queries
const quickStartQueries = [
  {
    question: "How many orders were placed last month?",
    description: "SQL query for order analytics",
    icon: CalendarIcon
  },
  {
    question: "Who are our top 5 customers by sales?",
    description: "Customer analysis query",
    icon: UsersIcon
  },
  {
    question: "What is our return policy?",
    description: "Search policy documents",
    icon: DocumentTextIcon
  },
  {
    question: "Show me sales trends by region",
    description: "Regional analytics",
    icon: ChartBarIcon
  }
]

// Messages for current conversation
const messages = computed(() => {
  return apiStore.queryHistory.map(query => ({
    id: query.id,
    question: query.question,
    result: query.result,
    timestamp: query.timestamp,
    type: query.type,
    error: query.error
  }))
})

// Utility functions
const formatDate = (date) => {
  return format(new Date(date), 'HH:mm')
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return new Intl.NumberFormat().format(value)
  }
  return String(value)
}

const getQueryTypeColor = (type) => {
  const colors = {
    sql: 'bg-blue-500',
    document: 'bg-green-500',
    policy_query: 'bg-green-500',
    unknown: 'bg-gray-500'
  }
  return colors[type] || colors.unknown
}

const getQueryTypeBadge = (type) => {
  const badges = {
    sql: 'bg-blue-100 text-blue-800',
    document: 'bg-green-100 text-green-800',
    policy_query: 'bg-green-100 text-green-800',
    unknown: 'bg-gray-100 text-gray-800'
  }
  return badges[type] || badges.unknown
}

// Message handling
const sendMessage = async (message) => {
  if (!message.trim()) return
  
  inputMessage.value = ''
  
  let result
  if (queryType.value === 'sql') {
    result = await apiStore.executeSqlQuery(message)
  } else if (queryType.value === 'document') {
    result = await apiStore.executeRagQuery(message)
  } else {
    // Auto-detect
    result = await apiStore.executeQuery(message)
  }
  
  // Scroll to bottom
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleSubmit = () => {
  sendMessage(inputMessage.value)
}

const loadQuery = (query) => {
  selectedQuery.value = query
}

const clearHistory = () => {
  apiStore.clearHistory()
  selectedQuery.value = null
}

// Handle URL query parameter
onMounted(() => {
  if (route.query.q) {
    inputMessage.value = route.query.q
    sendMessage(route.query.q)
  }
})
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 