<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Document Search</h1>
        <p class="text-gray-600">Search and manage policy documents using AI-powered retrieval</p>
      </div>
      <button
        @click="showUploadModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        <DocumentPlusIcon class="h-4 w-4 mr-2 inline" />
        Add Document
      </button>
    </div>

    <!-- Search Section -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Search Documents</h3>
      <form @submit.prevent="searchDocuments" class="space-y-4">
        <div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Ask a question about policies, procedures, or guidelines..."
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input
                v-model="searchType"
                type="radio"
                value="semantic"
                class="mr-2"
              />
              <span class="text-sm text-gray-700">Semantic Search</span>
            </label>
            <label class="flex items-center">
              <input
                v-model="searchType"
                type="radio"
                value="keyword"
                class="mr-2"
              />
              <span class="text-sm text-gray-700">Keyword Search</span>
            </label>
          </div>
          <button
            type="submit"
            :disabled="!searchQuery.trim() || apiStore.isLoading"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <MagnifyingGlassIcon class="h-4 w-4 mr-2 inline" />
            Search
          </button>
        </div>
      </form>
    </div>

    <!-- Quick Search Examples -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Common Questions</h3>
        <p class="text-sm text-gray-600 mt-1">Click on any question to search</p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            v-for="example in searchExamples"
            :key="example.question"
            @click="searchQuery = example.question; searchDocuments()"
            class="p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <div class="flex items-start">
              <component :is="example.icon" class="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-gray-900">{{ example.question }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ example.category }}</p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="bg-white rounded-lg shadow-sm border">
      <div class="p-6 border-b">
        <h3 class="text-lg font-semibold text-gray-900">Search Results</h3>
        <p class="text-sm text-gray-600 mt-1">{{ searchResults.length }} results found</p>
      </div>
      <div class="p-6 space-y-6">
        <div
          v-for="result in searchResults"
          :key="result.id"
          class="border border-gray-200 rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-3">
            <h4 class="text-sm font-semibold text-gray-900">{{ result.question }}</h4>
            <span class="text-xs text-gray-500">{{ formatDate(result.timestamp) }}</span>
          </div>

          <!-- Answer -->
          <div v-if="result.result.answer" class="mb-4">
            <div class="p-4 bg-blue-50 rounded-lg">
              <p class="text-sm text-blue-900">{{ result.result.answer }}</p>
            </div>
          </div>

          <!-- Sources -->
          <div v-if="result.result.sources && result.result.sources.length > 0" class="space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Sources:</h5>
            <div
              v-for="(source, index) in result.result.sources"
              :key="index"
              class="p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500"
            >
              <p class="text-sm text-gray-700">{{ source.text || source }}</p>
              <div v-if="source.metadata" class="mt-2 flex items-center space-x-4">
                <span class="text-xs text-gray-500">
                  <DocumentTextIcon class="h-3 w-3 inline mr-1" />
                  {{ source.metadata.source || 'Document' }}
                </span>
                <span v-if="source.metadata.page" class="text-xs text-gray-500">
                  Page {{ source.metadata.page }}
                </span>
                <span v-if="source.metadata.date" class="text-xs text-gray-500">
                  {{ formatDate(source.metadata.date) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Add Document</h3>
          <button
            @click="showUploadModal = false"
            class="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>

        <form @submit.prevent="uploadDocument" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Document Content
            </label>
            <textarea
              v-model="uploadForm.content"
              rows="6"
              placeholder="Paste your document content here..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Source Name
            </label>
            <input
              v-model="uploadForm.source"
              type="text"
              placeholder="e.g., Employee Handbook, Return Policy"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              v-model="uploadForm.category"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="policy">Policy</option>
              <option value="procedure">Procedure</option>
              <option value="guideline">Guideline</option>
              <option value="manual">Manual</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              @click="showUploadModal = false"
              class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="apiStore.isLoading"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <div v-if="apiStore.isLoading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline"></div>
              Add Document
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Document Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Documents</p>
            <p class="text-2xl font-bold text-gray-900">{{ documentStats.total || 0 }}</p>
          </div>
          <DocumentTextIcon class="h-8 w-8 text-blue-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Recent Searches</p>
            <p class="text-2xl font-bold text-gray-900">{{ searchResults.length }}</p>
          </div>
          <MagnifyingGlassIcon class="h-8 w-8 text-green-600" />
        </div>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-sm border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Categories</p>
            <p class="text-2xl font-bold text-gray-900">5</p>
          </div>
          <FolderIcon class="h-8 w-8 text-purple-600" />
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
  DocumentPlusIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  FolderIcon,
  QuestionMarkCircleIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon,
  TruckIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'

const apiStore = useApiStore()

const searchQuery = ref('')
const searchType = ref('semantic')
const searchResults = ref([])
const showUploadModal = ref(false)
const documentStats = ref({ total: 0 })

const uploadForm = ref({
  content: '',
  source: '',
  category: 'policy'
})

// Search examples
const searchExamples = [
  {
    question: "What is our return policy?",
    category: "Customer Service",
    icon: CurrencyDollarIcon
  },
  {
    question: "How do I request time off?",
    category: "HR Policies",
    icon: UserGroupIcon
  },
  {
    question: "What are the shipping guidelines?",
    category: "Operations",
    icon: TruckIcon
  },
  {
    question: "What is our data privacy policy?",
    category: "Security",
    icon: ShieldCheckIcon
  },
  {
    question: "How do I report a workplace incident?",
    category: "Safety",
    icon: QuestionMarkCircleIcon
  },
  {
    question: "What are the employee benefits?",
    category: "HR Policies",
    icon: UserGroupIcon
  }
]

// Utility functions
const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy HH:mm')
}

// Search documents
const searchDocuments = async () => {
  if (!searchQuery.value.trim()) return

  const result = await apiStore.executeRagQuery(searchQuery.value)
  if (result.success) {
    const searchResult = {
      id: Date.now(),
      question: searchQuery.value,
      result: result.data,
      timestamp: new Date()
    }
    
    searchResults.value.unshift(searchResult)
    
    // Keep only last 10 results
    if (searchResults.value.length > 10) {
      searchResults.value = searchResults.value.slice(0, 10)
    }
  }
}

// Upload document
const uploadDocument = async () => {
  const metadata = {
    source: uploadForm.value.source,
    category: uploadForm.value.category,
    date: new Date().toISOString(),
    uploaded_by: 'user'
  }

  const result = await apiStore.ingestDocument(uploadForm.value.content, metadata)
  if (result.success) {
    showUploadModal.value = false
    uploadForm.value = {
      content: '',
      source: '',
      category: 'policy'
    }
    
    // Update document stats
    documentStats.value.total += 1
  }
}

// Load document statistics
const loadDocumentStats = async () => {
  const result = await apiStore.fetchStats()
  if (result.success && result.data.statistics) {
    documentStats.value.total = result.data.statistics.policy_documents || 0
  }
}

onMounted(() => {
  loadDocumentStats()
})
</script> 