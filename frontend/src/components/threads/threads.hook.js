'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import Cookie from 'js-cookie'
import { useWebSocket } from '@/app/WebSocketContext'; 

export default function useThreads() {
  const { ws } = useWebSocket();
  const [chatThreads, setChatThreads] = useState([])
  const [selectedThread, setSelectedThread] = useState(null)
  const [showThreads, setShowThreads] = useState(false)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [pendingThreadId, setPendingThreadId] = useState(null);


  const fetchThreads = async (monthNumber,year,thread_id="") => {
    try {
      if (thread_id ===""){
      const Token = sessionStorage.getItem("admin_access_token");
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/thread/get_threads?month=${monthNumber}&year=${year}`,
        {
          headers: {
            "Authorization": Token || '', // <-- use your auth token
          },
        }
      );

      const result = res.data;
      return result
    }
      else{
        const Token = sessionStorage.getItem("admin_access_token");
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/thread/get_threads?thread_id=${thread_id}`,
        {
          headers: {
            "Authorization": Token || '', // <-- use your auth token
          },
        }
      );

      const result = res.data;
      return result

      }

    } catch (error) {
      console.error("Error fetching threads:", error);
    } finally {
      setLoading(false);
    }
  };

  // useEffect(() => {
  //   fetchThreads()
  // }, [])
  const toggleShowThreads = () => setShowThreads(prev => !prev)


  const createNewThread = async (lang) => {
    try {
      // const oldToken = Cookie.get('token');
      const oldToken = sessionStorage.getItem("guest_token");
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/thread/create_threads?lang=${lang}`, {
        headers: {
          Authorization: oldToken || '',
        },
      });
  
      const thread = response.data.thread;
  
      if (response.data.token?.access_token) {
        Cookie.set('token', response.data.token.access_token, {
          expires: 1,
          sameSite:'Strict'

        });
      }
  
      return thread; // only return thread
    } catch (error) {
      console.error('Failed to create new thread:', error);
      return null;
    }
  };


  const changeLanguage = async (threadId, lang) => {
  try {
    const oldToken = sessionStorage.getItem("guest_token");
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/thread/change_language`,
      {
        thread_id: threadId,
        language: lang,
      },
      {
        headers: {
          Authorization: oldToken || "",
        },
      }
    );

    return response.data; // return response data
  } catch (error) {
    console.error("Failed to send message to thread:", error);
    return null;
  }
};
  

  
  const selectThreadAndFetchData = async (thread) => {
    try {
      setSelectedThread(thread)
      toggleShowThreads()
      setLoading(true)
  
      const token = Cookie.get('token')
      
      const threadResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/thread/select_threads?thread_id=${thread._id}`, {
        headers: {
          Authorization: {token} || '',
        },
      })
  

      Cookie.set('token',threadResponse.data.msg.access_token,
        {
          expires:1,
          sameSite:"Strict"
        })
      const new_token=threadResponse.data.msg.access_token;


      const messageResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/message/get_all_messages/?thread_id=${thread._id}`, {
        headers: {
          Authorization: `Bearer ${new_token}` || '',
        },
      })

      const formattedMessages = messageResponse.data.messages.map((msg) => ({
        text: msg.content,
        sender: msg.role === 'user' ? 'user' : 'bot',
      }))

      setMessages(formattedMessages)
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'init',thread_id: thread._id }));
      } else {
        console.error('WebSocket not ready');
      }

      ws?.addEventListener('message', (event) => {
      });

    } catch (error) {
      console.error('Error fetching thread or messages:', error)
    } finally {
      setLoading(false)
    }
  }
  const handleDeleteChat = async (thread_id) => {
    try {
      const token = Cookie.get('token')
      
      
      const threadResponse = await axios.delete(`${process.env.NEXT_PUBLIC_API_BASE_URL}/thread/delete_thread?thread_id=${thread_id}`, {
        headers: {
          Authorization: `Bearer ${token}` || '',
        },
      })

      await fetchThreads()
  
    } catch (error) {
      console.error('Error fetching thread or messages:', error)
    }
  }
  const handleEditName = async (thread_id, thread_name) => {
    try {
      const token = Cookie.get('token');

  
      const threadResponse = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/thread/edit_name`,
        {
          name: thread_name,
          thread_id: thread_id
        },
        {
          headers: {
            Authorization: `Bearer ${token || ''}`,
          }
        }
      );

  
      await fetchThreads(); 
  
    } catch (error) {
      console.error('Error editing thread name:', error);
    }
  };
  

  return {
    chatThreads,
    selectedThread,
    setSelectedThread,
    createNewThread,
    selectThreadAndFetchData,
    messages,
    setMessages,
    setChatThreads,
    setShowThreads,
    fetchThreads,
    handleDeleteChat,
    handleEditName,
    changeLanguage
  }
}
