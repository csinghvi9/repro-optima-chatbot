'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import Cookies from 'js-cookie'

export default function useMessages(selectedThread) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchMessages = async () => {
      if (!selectedThread) return

      setLoading(true)

      try {
        const token = Cookies.get('access_token') 
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/message/get_all_messages/`, {
            headers: {
              Authorization:`Bearer ${token}`|| '',
            },
          })

        const formattedMessages = res.data.messages.map((msg) => ({
          text: msg.content,
          sender: msg.role === 'user' ? 'user' : 'bot', 
        }))

        setMessages(formattedMessages)
      } catch (error) {
        console.error('Failed to fetch messages:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMessages()
  }, [selectedThread])

  return { messages, setMessages, loading }
}
