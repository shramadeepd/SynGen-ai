<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Loading overlay -->
    <div v-if="authStore.isLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-2 text-gray-600">Loading...</p>
      </div>
    </div>

    <!-- Main layout for authenticated users -->
    <div v-if="authStore.isAuthenticated" class="flex h-screen">
      <!-- Sidebar -->
      <div class="w-64 bg-white shadow-lg">
        <div class="p-4 border-b">
          <h1 class="text-xl font-bold text-gray-800">SynGen AI</h1>
          <p class="text-sm text-gray-600">Intelligent Analytics</p>
        </div>
        
        <nav class="mt-4">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            class="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors"
            :class="{ 'bg-blue-50 text-blue-700 border-r-2 border-blue-700': $route.name === item.name }"
          >
            <component :is="item.icon" class="h-5 w-5 mr-3" />
            {{ item.name }}
          </router-link>
        </nav>

        <!-- User info and logout -->
        <div class="absolute bottom-0 w-64 p-4 border-t bg-gray-50">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700">{{ authStore.userName }}</p>
              <p class="text-xs text-gray-500">{{ authStore.userRole }}</p>
            </div>
            <button
              @click="handleLogout"
              class="text-gray-400 hover:text-gray-600 transition-colors"
              title="Logout"
            >
              <LogOutIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b px-6 py-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-800">{{ currentPageTitle }}</h2>
            <div class="flex items-center space-x-4">
              <!-- Health status indicator -->
              <div class="flex items-center space-x-2">
                <div class="h-2 w-2 bg-green-500 rounded-full"></div>
                <span class="text-sm text-gray-600">System Online</span>
              </div>
            </div>
          </div>
        </header>

        <!-- Page content -->
        <main class="flex-1 overflow-auto">
          <router-view />
        </main>
      </div>
    </div>

    <!-- Login view for unauthenticated users -->
    <div v-else>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import {
  HomeIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CogIcon,
  ArrowLeftOnRectangleIcon as LogOutIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Navigation items
const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Documents', href: '/documents', icon: DocumentTextIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon }
]

// Current page title
const currentPageTitle = computed(() => {
  const currentNav = navigation.find(item => item.name === route.name)
  return currentNav ? currentNav.name : 'SynGen AI'
})

// Handle logout
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Initialize authentication on app start
onMounted(async () => {
  await authStore.initializeAuth()
})
</script>

<style scoped>
/* Custom scrollbar for main content */
main::-webkit-scrollbar {
  width: 6px;
}

main::-webkit-scrollbar-track {
  background: #f1f1f1;
}

main::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

main::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Router link active state */
.router-link-active {
  @apply bg-blue-50 text-blue-700 border-r-2 border-blue-700;
}
</style>