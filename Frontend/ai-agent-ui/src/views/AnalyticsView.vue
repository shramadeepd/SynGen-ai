<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p class="text-gray-600">Explore your supply chain data with interactive visualizations</p>
      </div>
      <button
        @click="refreshData"
        :disabled="isLoading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        <ArrowPathIcon class="h-4 w-4 mr-2 inline" :class="{ 'animate-spin': isLoading }" />
        Refresh Data
      </button>
    </div>

    <!-- Key Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Revenue</p>
            <p class="text-2xl font-bold text-gray-900">${{ formatNumber(stats?.total_sales || 0) }}</p>
            <p class="text-sm text-green-600 mt-1">↗ 12.5% from last month</p>
          </div>
          <CurrencyDollarIcon class="h-8 w-8 text-green-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Orders</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(stats?.orders || 0) }}</p>
            <p class="text-sm text-blue-600 mt-1">↗ 8.2% from last month</p>
          </div>
          <ShoppingCartIcon class="h-8 w-8 text-blue-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Active Customers</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(stats?.customers || 0) }}</p>
            <p class="text-sm text-purple-600 mt-1">↗ 5.1% from last month</p>
          </div>
          <UsersIcon class="h-8 w-8 text-purple-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Products</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(stats?.products || 0) }}</p>
            <p class="text-sm text-orange-600 mt-1">→ No change</p>
          </div>
          <CubeIcon class="h-8 w-8 text-orange-600" />
        </div>
      </div>
    </div>

    <!-- Quick Analytics Queries -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Quick Analytics</h3>
        <p class="text-sm text-gray-600 mt-1">Run common analytics queries with one click</p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            v-for="query in analyticsQueries"
            :key="query.title"
            @click="runAnalyticsQuery(query.question)"
            :disabled="apiStore.isLoading"
            class="p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors disabled:opacity-50"
          >
            <div class="flex items-start">
              <component :is="query.icon" class="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-gray-900">{{ query.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ query.description }}</p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Recent Analytics Results -->
    <div v-if="analyticsResults.length > 0" class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Recent Analytics Results</h3>
      </div>
      <div class="p-6 space-y-6">
        <div
          v-for="result in analyticsResults"
          :key="result.id"
          class="border border-gray-200 rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-semibold text-gray-900">{{ result.question }}</h4>
            <span class="text-xs text-gray-500">{{ formatDate(result.timestamp) }}</span>
          </div>

          <!-- SQL Results Table -->
          <div v-if="result.result.rows && result.result.rows.length > 0" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-md">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    v-for="(value, key) in result.result.rows[0]"
                    :key="key"
                    class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {{ key }}
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(row, index) in result.result.rows.slice(0, 5)" :key="index">
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
            <div v-if="result.result.rows.length > 5" class="text-xs text-gray-500 mt-2 text-center">
              Showing first 5 of {{ result.result.rows.length }} results
            </div>
          </div>

          <!-- Explanation -->
          <div v-if="result.result.explanation" class="mt-3 p-3 bg-blue-50 rounded-md">
            <p class="text-sm text-blue-800">{{ result.result.explanation }}</p>
          </div>

          <!-- View in Chat button -->
          <div class="mt-3 flex justify-end">
            <router-link
              :to="{ path: '/chat', query: { q: result.question } }"
              class="text-sm text-blue-600 hover:text-blue-700"
            >
              View in Chat →
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Insights -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Customers -->
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="p-6 border-b">
          <h3 class="text-lg font-semibold text-gray-900">Top Customers</h3>
        </div>
        <div class="p-6">
          <div v-if="topCustomers.length === 0" class="text-center py-8">
            <UsersIcon class="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500">No customer data available</p>
            <button
              @click="loadTopCustomers"
              class="mt-2 text-sm text-blue-600 hover:text-blue-700"
            >
              Load Customer Data
            </button>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(customer, index) in topCustomers"
              :key="customer.customer_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <span class="text-sm font-medium text-blue-600">{{ index + 1 }}</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">
                    {{ customer.first_name }} {{ customer.last_name }}
                  </p>
                  <p class="text-xs text-gray-500">{{ customer.segment }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-900">${{ formatNumber(customer.total_sales) }}</p>
                <p class="text-xs text-gray-500">{{ customer.order_count }} orders</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Orders -->
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="p-6 border-b">
          <h3 class="text-lg font-semibold text-gray-900">Recent Orders</h3>
        </div>
        <div class="p-6">
          <div v-if="recentOrders.length === 0" class="text-center py-8">
            <ShoppingCartIcon class="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500">No recent orders available</p>
            <button
              @click="loadRecentOrders"
              class="mt-2 text-sm text-blue-600 hover:text-blue-700"
            >
              Load Order Data
            </button>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="order in recentOrders"
              :key="order.order_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <p class="text-sm font-medium text-gray-900">Order #{{ order.order_id }}</p>
                <p class="text-xs text-gray-500">{{ formatDate(order.order_date) }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-900">${{ formatNumber(order.total_amount) }}</p>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {{ order.delivery_status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApiStore } from '../stores/api'
import { format } from 'date-fns'
import {
  ArrowPathIcon,
  CurrencyDollarIcon,
  ShoppingCartIcon,
  UsersIcon,
  CubeIcon,
  ChartBarIcon,
  CalendarIcon,
  TruckIcon,
  BuildingStorefrontIcon,
  MapIcon
} from '@heroicons/vue/24/outline'

const apiStore = useApiStore()

const isLoading = ref(false)
const stats = ref(null)
const analyticsResults = ref([])
const topCustomers = ref([])
const recentOrders = ref([])

// Analytics queries
const analyticsQueries = [
  {
    title: "Sales by Region",
    description: "Analyze sales performance by geographic region",
    question: "Show me total sales by region",
    icon: MapIcon
  },
  {
    title: "Monthly Trends",
    description: "View sales trends over the last 12 months",
    question: "Show me monthly sales trends for the last year",
    icon: CalendarIcon
  },
  {
    title: "Top Products",
    description: "Find best-selling products by revenue",
    question: "What are the top 10 products by sales revenue?",
    icon: CubeIcon
  },
  {
    title: "Customer Segments",
    description: "Analyze customer distribution by segment",
    question: "Show me customer count and average sales by segment",
    icon: UsersIcon
  },
  {
    title: "Delivery Performance",
    description: "Analyze shipping and delivery metrics",
    question: "Show me delivery performance metrics by shipping mode",
    icon: TruckIcon
  },
  {
    title: "Profit Analysis",
    description: "Analyze profit margins by product category",
    question: "Show me profit margins by product category",
    icon: ChartBarIcon
  }
]

// Utility functions
const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return new Intl.NumberFormat().format(value)
  }
  return String(value)
}

// Data loading functions
const refreshData = async () => {
  isLoading.value = true
  try {
    const result = await apiStore.fetchStats()
    if (result.success) {
      stats.value = result.data.statistics
    }
  } finally {
    isLoading.value = false
  }
}

const runAnalyticsQuery = async (question) => {
  const result = await apiStore.executeSqlQuery(question)
  if (result.success) {
    analyticsResults.value.unshift({
      id: Date.now(),
      question,
      result: result.data,
      timestamp: new Date()
    })
    
    // Keep only last 5 results
    if (analyticsResults.value.length > 5) {
      analyticsResults.value = analyticsResults.value.slice(0, 5)
    }
  }
}

const loadTopCustomers = async () => {
  const result = await apiStore.executeSqlQuery("SELECT c.customer_id, c.first_name, c.last_name, c.segment, SUM(oi.sales) as total_sales, COUNT(DISTINCT o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id, c.first_name, c.last_name, c.segment ORDER BY total_sales DESC LIMIT 5")
  if (result.success && result.data.rows) {
    topCustomers.value = result.data.rows
  }
}

const loadRecentOrders = async () => {
  const result = await apiStore.executeSqlQuery("SELECT o.order_id, o.order_date, SUM(oi.sales) as total_amount, ds.delivery_status FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN delivery_statuses ds ON o.delivery_status_id = ds.delivery_status_id GROUP BY o.order_id, o.order_date, ds.delivery_status ORDER BY o.order_date DESC LIMIT 5")
  if (result.success && result.data.rows) {
    recentOrders.value = result.data.rows
  }
}

// Load data on mount
onMounted(async () => {
  await refreshData()
  await loadTopCustomers()
  await loadRecentOrders()
})
</script> 