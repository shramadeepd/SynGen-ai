import { ref, computed } from 'vue'

const useChat = () => {
  const messages = ref([])
  const isLoading = ref(false)

  const responses = [
    "I've analyzed the market trends and it appears that demand for your product category is growing at 12% annually.",
    "Based on the information you've shared, I'd recommend focusing on improving customer retention strategies first.",
    "Your business could benefit from expanding into these three adjacent markets based on your current strengths.",
    "The competitive analysis shows that your pricing strategy is optimal for your current market position.",
    "I can help you draft a strategic plan for the next quarter. What specific goals would you like to focus on?",
    "The data suggests that your customer acquisition cost could be reduced by implementing targeted social media campaigns.",
    "Looking at your business model, I see opportunities for increased efficiency in your supply chain management.",
  ]

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) return
    
    const userMsg = {
      content: userMessage,
      isUser: true,
      timestamp: new Date()
    }
    
    messages.value.push(userMsg)
    isLoading.value = true
    
    setTimeout(() => {
      const randomResponse = responses[Math.floor(Math.random() * responses.length)]
      
      const aiMsg = {
        content: randomResponse,
        isUser: false,
        timestamp: new Date()
      }
      
      messages.value.push(aiMsg)
      isLoading.value = false
    }, 1500)
  }

  return {
    messages: computed(() => messages.value),
    isLoading: computed(() => isLoading.value),
    sendMessage
  }
}

export { useChat }