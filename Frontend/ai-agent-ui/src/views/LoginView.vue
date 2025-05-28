<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full space-y-8 p-8">
      <!-- Logo and title -->
      <div class="text-center">
        <div class="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
          <ChartBarIcon class="h-8 w-8 text-white" />
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          SynGen AI
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Intelligent Text-to-SQL Analytics Platform
        </p>
      </div>

      <!-- Login form -->
      <div class="bg-white rounded-lg shadow-lg p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="authStore.isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div v-if="authStore.isLoading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {{ authStore.isLoading ? 'Signing in...' : 'Sign in' }}
            </button>
          </div>
        </form>

        <!-- Demo credentials -->
        <div class="mt-6 p-4 bg-gray-50 rounded-md">
          <h3 class="text-sm font-medium text-gray-700 mb-2">Demo Credentials:</h3>
          <div class="space-y-1 text-xs text-gray-600">
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Analyst:</strong> analyst / analyst123</p>
          </div>
        </div>

        <!-- Quick login buttons -->
        <div class="mt-4 grid grid-cols-2 gap-3">
          <button
            @click="quickLogin('admin')"
            :disabled="authStore.isLoading"
            class="px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 disabled:opacity-50"
          >
            Login as Admin
          </button>
          <button
            @click="quickLogin('analyst')"
            :disabled="authStore.isLoading"
            class="px-3 py-2 text-xs font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 disabled:opacity-50"
          >
            Login as Analyst
          </button>
        </div>
      </div>

      <!-- Features -->
      <div class="text-center">
        <div class="grid grid-cols-3 gap-4 mt-8">
          <div class="text-center">
            <ChatBubbleLeftRightIcon class="h-6 w-6 text-blue-600 mx-auto mb-2" />
            <p class="text-xs text-gray-600">Natural Language Queries</p>
          </div>
          <div class="text-center">
            <DocumentTextIcon class="h-6 w-6 text-blue-600 mx-auto mb-2" />
            <p class="text-xs text-gray-600">Document Search</p>
          </div>
          <div class="text-center">
            <ChartBarIcon class="h-6 w-6 text-blue-600 mx-auto mb-2" />
            <p class="text-xs text-gray-600">Real-time Analytics</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  const result = await authStore.login(form.value)
  if (result.success) {
    router.push('/dashboard')
  }
}

const quickLogin = async (role) => {
  const credentials = {
    admin: { username: 'admin', password: 'admin123' },
    analyst: { username: 'analyst', password: 'analyst123' }
  }
  
  form.value = credentials[role]
  await handleLogin()
}
</script> 