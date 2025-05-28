import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export const useApiStore = defineStore('api', () => {
  const toast = useToast()
  
  // State
  const isLoading = ref(false)
  const queryHistory = ref([])
  const systemStats = ref(null)

  // Query API
  const executeQuery = async (question) => {
    isLoading.value = true
    try {
      const response = await axios.post('/api/query', { question })
      
      // Add to history
      const queryResult = {
        id: Date.now(),
        question,
        result: response.data,
        timestamp: new Date(),
        type: response.data.type || 'unknown'
      }
      
      queryHistory.value.unshift(queryResult)
      
      // Keep only last 50 queries
      if (queryHistory.value.length > 50) {
        queryHistory.value = queryHistory.value.slice(0, 50)
      }
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Query error:', error)
      const message = error.response?.data?.detail || 'Query failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  // SQL-specific query
  const executeSqlQuery = async (question) => {
    isLoading.value = true
    try {
      const response = await axios.post('/api/sql', { question })
      
      const queryResult = {
        id: Date.now(),
        question,
        result: response.data,
        timestamp: new Date(),
        type: 'sql'
      }
      
      queryHistory.value.unshift(queryResult)
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('SQL query error:', error)
      const message = error.response?.data?.detail || 'SQL query failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  // RAG query for documents
  const executeRagQuery = async (question) => {
    isLoading.value = true
    try {
      const response = await axios.post('/api/rag/query', { question })
      
      const queryResult = {
        id: Date.now(),
        question,
        result: response.data,
        timestamp: new Date(),
        type: 'document'
      }
      
      queryHistory.value.unshift(queryResult)
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('RAG query error:', error)
      const message = error.response?.data?.detail || 'Document query failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  // Ingest document
  const ingestDocument = async (document, metadata = {}) => {
    isLoading.value = true
    try {
      const response = await axios.post('/api/rag/ingest', {
        document,
        metadata
      })
      
      toast.success('Document ingested successfully')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Document ingest error:', error)
      const message = error.response?.data?.detail || 'Document ingest failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  // Get database statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats')
      systemStats.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Stats fetch error:', error)
      return { success: false, error: 'Failed to fetch statistics' }
    }
  }

  // Get system statistics
  const fetchSystemStats = async () => {
    try {
      const response = await axios.get('/api/system/stats')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('System stats fetch error:', error)
      return { success: false, error: 'Failed to fetch system statistics' }
    }
  }

  // Health check
  const checkHealth = async () => {
    try {
      const response = await axios.get('/health')
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Health check error:', error)
      return { success: false, error: 'Health check failed' }
    }
  }

  // Clear query history
  const clearHistory = () => {
    queryHistory.value = []
    toast.info('Query history cleared')
  }

  // Get query by ID
  const getQueryById = (id) => {
    return queryHistory.value.find(query => query.id === id)
  }

  // Get queries by type
  const getQueriesByType = (type) => {
    return queryHistory.value.filter(query => query.type === type)
  }

  return {
    // State
    isLoading,
    queryHistory,
    systemStats,
    // Actions
    executeQuery,
    executeSqlQuery,
    executeRagQuery,
    ingestDocument,
    fetchStats,
    fetchSystemStats,
    checkHealth,
    clearHistory,
    getQueryById,
    getQueriesByType
  }
}) 