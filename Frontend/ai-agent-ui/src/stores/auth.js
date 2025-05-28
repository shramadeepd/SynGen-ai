import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export const useAuthStore = defineStore('auth', () => {
  const toast = useToast()
  
  // State
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || 'user')
  const userName = computed(() => user.value?.username || 'User')

  // Actions
  const login = async (credentials) => {
    isLoading.value = true
    try {
      // Create form data for the backend
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response = await axios.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const { access_token } = response.data
      
      // Store token
      token.value = access_token
      localStorage.setItem('token', access_token)

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      // Get user info
      await fetchUserInfo()

      toast.success('Login successful!')
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      await axios.post('/auth/register', userData)
      toast.success('Registration successful! Please login.')
      return { success: true }
    } catch (error) {
      console.error('Registration error:', error)
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get('/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      // If fetching user info fails, create a basic user object
      const basicUser = {
        username: 'user',
        role: 'user',
        region: 'global'
      }
      user.value = basicUser
      localStorage.setItem('user', JSON.stringify(basicUser))
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
    toast.info('Logged out successfully')
  }

  const initializeAuth = async () => {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      if (!user.value) {
        await fetchUserInfo()
      }
    }
  }

  return {
    // State
    token,
    user,
    isLoading,
    // Getters
    isAuthenticated,
    userRole,
    userName,
    // Actions
    login,
    register,
    logout,
    fetchUserInfo,
    initializeAuth
  }
}) 