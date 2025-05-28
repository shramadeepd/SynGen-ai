<template>
  <div class="p-6 space-y-6">
    <!-- Welcome section -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
      <h1 class="text-2xl font-bold mb-2">Welcome back, {{ authStore.userName }}!</h1>
      <p class="text-blue-100">Ready to analyze your supply chain data with AI-powered insights.</p>
    </div>

    <!-- Quick actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <router-link
        to="/chat"
        class="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
      >
        <div class="flex items-center">
          <div class="p-3 bg-blue-100 rounded-lg">
            <ChatBubbleLeftRightIcon class="h-6 w-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-gray-900">Start Chatting</h3>
            <p class="text-gray-600">Ask questions in natural language</p>
          </div>
        </div>
      </router-link>

      <router-link
        to="/analytics"
        class="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
      >
        <div class="flex items-center">
          <div class="p-3 bg-green-100 rounded-lg">
            <ChartBarIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-gray-900">View Analytics</h3>
            <p class="text-gray-600">Explore data visualizations</p>
          </div>
        </div>
      </router-link>

      <router-link
        to="/documents"
        class="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
      >
        <div class="flex items-center">
          <div class="p-3 bg-purple-100 rounded-lg">
            <DocumentTextIcon class="h-6 w-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-semibold text-gray-900">Search Documents</h3>
            <p class="text-gray-600">Find policy information</p>
          </div>
        </div>
      </router-link>
    </div>

    <!-- Statistics cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Customers</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats?.statistics?.customers || 0 }}</p>
          </div>
          <UsersIcon class="h-8 w-8 text-blue-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Products</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats?.statistics?.products || 0 }}</p>
          </div>
          <CubeIcon class="h-8 w-8 text-green-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Orders</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats?.statistics?.orders || 0 }}</p>
          </div>
          <ShoppingCartIcon class="h-8 w-8 text-purple-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Sales</p>
            <p class="text-2xl font-bold text-gray-900">${{ formatNumber(stats?.statistics?.total_sales || 0) }}</p>
          </div>
          <CurrencyDollarIcon class="h-8 w-8 text-yellow-600" />
        </div>
      </div>
    </div>

    <!-- Recent queries and system status -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent queries -->
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="p-6 border-b">
          <h3 class="text-lg font-semibold text-gray-900">Recent Queries</h3>
        </div>
        <div class="p-6">
          <div v-if="apiStore.queryHistory.length === 0" class="text-center py-8">
            <ChatBubbleLeftRightIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">No queries yet. Start by asking a question!</p>
            <router-link
              to="/chat"
              class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Start Chatting
            </router-link>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="query in recentQueries"
              :key="query.id"
              class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex-shrink-0">
                <div class="w-2 h-2 rounded-full mt-2" :class="getQueryTypeColor(query.type)"></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ query.question }}</p>
                <p class="text-xs text-gray-500">{{ formatDate(query.timestamp) }}</p>
              </div>
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" :class="getQueryTypeBadge(query.type)">
                {{ query.type }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- System status -->
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="p-6 border-b">
          <h3 class="text-lg font-semibold text-gray-900">System Status</h3>
        </div>
        <div class="p-6 space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Database Connection</span>
            <div class="flex items-center">
              <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm text-green-600">Connected</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">AI Services</span>
            <div class="flex items-center">
              <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm text-green-600">Online</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Document Store</span>
            <div class="flex items-center">
              <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm text-green-600">{{ stats?.statistics?.policy_documents || 0 }} docs</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Query Cache</span>
            <div class="flex items-center">
              <div class="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              <span class="text-sm text-blue-600">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sample queries -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Try These Sample Queries</h3>
        <p class="text-sm text-gray-600 mt-1">Click on any question to try it out</p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            v-for="sample in sampleQueries"
            :key="sample.question"
            @click="trySampleQuery(sample.question)"
            class="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useApiStore } from '../stores/api'
import { format } from 'date-fns'
import {
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  DocumentTextIcon,
  UsersIcon,
  CubeIcon,
  ShoppingCartIcon,
  CurrencyDollarIcon,
  TruckIcon,
  CalendarIcon,
  MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const apiStore = useApiStore()

const stats = ref(null)

// Sample queries
const sampleQueries = [
  {
    question: "How many orders were placed last month?",
    description: "Get order count for recent period",
    icon: CalendarIcon
  },
  {
    question: "Who are our top 5 customers by sales?",
    description: "Find highest value customers",
    icon: UsersIcon
  },
  {
    question: "What products have low inventory?",
    description: "Identify stock issues",
    icon: CubeIcon
  },
  {
    question: "Show me delivery performance metrics",
    description: "Analyze shipping efficiency",
    icon: TruckIcon
  },
  {
    question: "What is our return policy?",
    description: "Search policy documents",
    icon: DocumentTextIcon
  },
  {
    question: "Find products with highest profit margins",
    description: "Analyze product profitability",
    icon: ChartBarIcon
  }
]

// Recent queries (last 5)
const recentQueries = computed(() => {
  return apiStore.queryHistory.slice(0, 5)
})

// Utility functions
const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, HH:mm')
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

const trySampleQuery = (question) => {
  router.push({ path: '/chat', query: { q: question } })
}

// Load data on mount
onMounted(async () => {
  const result = await apiStore.fetchStats()
  if (result.success) {
    stats.value = result.data
  }
})
</script> 