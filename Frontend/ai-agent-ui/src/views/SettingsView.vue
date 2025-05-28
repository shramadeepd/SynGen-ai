<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
      <p class="text-gray-600">Manage your account and application preferences</p>
    </div>

    <!-- User Profile -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">User Profile</h3>
      </div>
      <div class="p-6">
        <div class="flex items-center space-x-6">
          <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
            <UserIcon class="h-10 w-10 text-blue-600" />
          </div>
          <div class="flex-1">
            <h4 class="text-lg font-semibold text-gray-900">{{ authStore.userName }}</h4>
            <p class="text-gray-600">{{ authStore.userRole }}</p>
            <p class="text-sm text-gray-500 mt-1">Last login: {{ formatDate(new Date()) }}</p>
          </div>
          <button class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            Edit Profile
          </button>
        </div>
      </div>
    </div>

    <!-- Application Preferences -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Application Preferences</h3>
      </div>
      <div class="p-6 space-y-6">
        <!-- Theme -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Theme</h4>
            <p class="text-sm text-gray-500">Choose your preferred color scheme</p>
          </div>
          <select
            v-model="preferences.theme"
            @change="updatePreferences"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>

        <!-- Default Query Type -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Default Query Type</h4>
            <p class="text-sm text-gray-500">Preferred query processing method</p>
          </div>
          <select
            v-model="preferences.defaultQueryType"
            @change="updatePreferences"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="auto">Auto-detect</option>
            <option value="sql">SQL Query</option>
            <option value="document">Document Search</option>
          </select>
        </div>

        <!-- Notifications -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Email Notifications</h4>
            <p class="text-sm text-gray-500">Receive updates about your queries</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              v-model="preferences.emailNotifications"
              @change="updatePreferences"
              type="checkbox"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <!-- Auto-save -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Auto-save Queries</h4>
            <p class="text-sm text-gray-500">Automatically save query history</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              v-model="preferences.autoSave"
              @change="updatePreferences"
              type="checkbox"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- System Information -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">System Information</h3>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="text-sm font-medium text-gray-900 mb-3">Application</h4>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Version:</span>
                <span class="text-gray-900">1.0.0</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Build:</span>
                <span class="text-gray-900">{{ new Date().toISOString().split('T')[0] }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Environment:</span>
                <span class="text-gray-900">Production</span>
              </div>
            </div>
          </div>

          <div>
            <h4 class="text-sm font-medium text-gray-900 mb-3">Database</h4>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">PostgreSQL:</span>
                <span class="flex items-center">
                  <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span class="text-green-600">Connected</span>
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">MongoDB:</span>
                <span class="flex items-center">
                  <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span class="text-green-600">Connected</span>
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Cache:</span>
                <span class="flex items-center">
                  <div class="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                  <span class="text-blue-600">Active</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Query Statistics -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Query Statistics</h3>
          <button
            @click="clearAllData"
            class="text-sm text-red-600 hover:text-red-700"
          >
            Clear All Data
          </button>
        </div>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-900">{{ apiStore.queryHistory.length }}</div>
            <div class="text-sm text-gray-600">Total Queries</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-900">{{ sqlQueries.length }}</div>
            <div class="text-sm text-gray-600">SQL Queries</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-900">{{ documentQueries.length }}</div>
            <div class="text-sm text-gray-600">Document Searches</div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="mt-6">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Recent Activity</h4>
          <div class="space-y-2">
            <div
              v-for="query in recentQueries"
              :key="query.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center">
                <div class="w-2 h-2 rounded-full mr-3" :class="getQueryTypeColor(query.type)"></div>
                <span class="text-sm text-gray-900 truncate">{{ query.question }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ formatDate(query.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Management -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Data Management</h3>
      </div>
      <div class="p-6 space-y-4">
        <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Export Query History</h4>
            <p class="text-sm text-gray-500">Download your query history as JSON</p>
          </div>
          <button
            @click="exportData"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <ArrowDownTrayIcon class="h-4 w-4 mr-2 inline" />
            Export
          </button>
        </div>

        <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Clear Cache</h4>
            <p class="text-sm text-gray-500">Clear application cache and temporary data</p>
          </div>
          <button
            @click="clearCache"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <TrashIcon class="h-4 w-4 mr-2 inline" />
            Clear
          </button>
        </div>

        <div class="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
          <div>
            <h4 class="text-sm font-medium text-red-900">Reset Application</h4>
            <p class="text-sm text-red-600">Reset all settings and clear all data</p>
          </div>
          <button
            @click="resetApplication"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            <ExclamationTriangleIcon class="h-4 w-4 mr-2 inline" />
            Reset
          </button>
        </div>
      </div>
    </div>

    <!-- About -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">About SynGen AI</h3>
      </div>
      <div class="p-6">
        <div class="prose prose-sm max-w-none">
          <p class="text-gray-600">
            SynGen AI is an intelligent Text-to-SQL platform that converts natural language questions 
            into accurate SQL queries and provides document search capabilities. Built with modern 
            AI technologies and enterprise-grade security.
          </p>
          <div class="mt-4 flex items-center space-x-4">
            <a href="#" class="text-blue-600 hover:text-blue-700 text-sm">Documentation</a>
            <a href="#" class="text-blue-600 hover:text-blue-700 text-sm">Support</a>
            <a href="#" class="text-blue-600 hover:text-blue-700 text-sm">Privacy Policy</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useApiStore } from '../stores/api'
import { useToast } from 'vue-toastification'
import { format } from 'date-fns'
import {
  UserIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const apiStore = useApiStore()
const toast = useToast()

const preferences = ref({
  theme: 'light',
  defaultQueryType: 'auto',
  emailNotifications: true,
  autoSave: true
})

// Computed properties
const sqlQueries = computed(() => {
  return apiStore.getQueriesByType('sql')
})

const documentQueries = computed(() => {
  return apiStore.getQueriesByType('document').concat(
    apiStore.getQueriesByType('policy_query')
  )
})

const recentQueries = computed(() => {
  return apiStore.queryHistory.slice(0, 5)
})

// Utility functions
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

// Settings functions
const updatePreferences = () => {
  localStorage.setItem('syngen_preferences', JSON.stringify(preferences.value))
  toast.success('Preferences updated')
}

const loadPreferences = () => {
  const saved = localStorage.getItem('syngen_preferences')
  if (saved) {
    preferences.value = { ...preferences.value, ...JSON.parse(saved) }
  }
}

const exportData = () => {
  const data = {
    queryHistory: apiStore.queryHistory,
    preferences: preferences.value,
    exportDate: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `syngen-ai-export-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  toast.success('Data exported successfully')
}

const clearCache = () => {
  // Clear various caches
  localStorage.removeItem('syngen_cache')
  sessionStorage.clear()
  
  toast.success('Cache cleared')
}

const clearAllData = () => {
  if (confirm('Are you sure you want to clear all query history? This action cannot be undone.')) {
    apiStore.clearHistory()
    toast.success('All data cleared')
  }
}

const resetApplication = () => {
  if (confirm('Are you sure you want to reset the application? This will clear all data and settings.')) {
    // Clear all local storage
    localStorage.clear()
    sessionStorage.clear()
    
    // Clear query history
    apiStore.clearHistory()
    
    // Reset preferences
    preferences.value = {
      theme: 'light',
      defaultQueryType: 'auto',
      emailNotifications: true,
      autoSave: true
    }
    
    toast.success('Application reset successfully')
  }
}

onMounted(() => {
  loadPreferences()
})
</script> 