"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import Chatbot from "@/components/container/home_page/bot_ui";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";
import { motion, AnimatePresence } from "framer-motion";

const ChatIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    className="w-7 h-7"
  >
    <path
      d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5Z"
      fill="white"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <circle cx="9" cy="11.5" r="1" fill="#CE3149" />
    <circle cx="12.5" cy="11.5" r="1" fill="#CE3149" />
    <circle cx="16" cy="11.5" r="1" fill="#CE3149" />
  </svg>
);

const CloseIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    className="w-6 h-6"
  >
    <path
      d="M18 6L6 18M6 6l12 12"
      stroke="white"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const ChatbotWidget: React.FC = () => {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [isLoadingChatbot, setIsLoadingChatbot] = useState(false);
  const { setUpWebSocket, disconnectWebSocket, isConnected } = useWebSocket();
  const [newThreadID, setThreadID] = useState<string | undefined>(undefined);
  const { createNewThread } = useThreads();

  const toggleChatbot = () => {
    if (isChatbotOpen) {
      disconnectWebSocket();
      setThreadID(undefined);
      setIsChatbotOpen(false);
      window.parent.postMessage({ type: "CHATBOT_CLOSE" }, "*");
    } else {
      setIsChatbotOpen(true);
      window.parent.postMessage({ type: "CHATBOT_OPEN" }, "*");
    }
  };
  useEffect(() => {}, [isConnected]);
  // Function to check if JWT token is expired
  const isTokenExpired = (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split(".")[1])) as {
        expires: number;
      };
      const exp = payload.expires; // expiration time (in seconds)
      const now = Math.floor(Date.now() / 1000);
      return now >= exp;
    } catch {
      return true; // If decoding fails, treat as expired
    }
  };

  useEffect(() => {
    const fetchGuestToken = async () => {
      try {
        setIsLoadingChatbot(true);
        let token = sessionStorage.getItem("guest_token");
        if (!token || isTokenExpired(token)) {
          const response = await axios.get(
            `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/guest_token`
          );
          token = response.data?.token?.access_token;
          if (token) sessionStorage.setItem("guest_token", token);
        }

        if (token) {
          setUpWebSocket(token);
          const newThread = await createNewThread("English");
          setThreadID(newThread._id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoadingChatbot(false);
      }
    };

    if (isChatbotOpen && !newThreadID && !isLoadingChatbot) {
      fetchGuestToken();
    }
  }, [
    isChatbotOpen,
    newThreadID,
    isLoadingChatbot,
    setUpWebSocket,
    createNewThread,
  ]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState !== "visible" || !isChatbotOpen) return;

      const token = sessionStorage.getItem("guest_token");

      // token dead => close bot & reset
      if (!token || isTokenExpired(token)) {
        disconnectWebSocket();
        sessionStorage.removeItem("guest_token");
        setThreadID(undefined);
        setIsChatbotOpen(false);
        window.parent.postMessage({ type: "CHATBOT_CLOSE" }, "*");
        return;
      }

      // token ok => reconnect
      setUpWebSocket(token);
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [isChatbotOpen, disconnectWebSocket, setUpWebSocket]);

  const showTooltip = !isChatbotOpen && !isLoadingChatbot;

  return (
    <div
      className="min-h-screen w-full relative overflow-hidden"
      style={{
        backgroundImage: "url('/clinic-bg.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Semi-transparent overlay for readability */}
      <div className="absolute inset-0 bg-white/60 pointer-events-none" />
      {/* Centered logo */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <img
          src="/Repro Logo.png"
          alt="Repro Optima"
          className="w-[180px] md:w-[260px] lg:w-[320px] drop-shadow-sm"
        />
      </div>
      {/* Chatbot Widget Popup */}
      <AnimatePresence>
        {newThreadID && (
          <motion.div
            initial={{ scale: 0.5, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.5, opacity: 0, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="fixed bottom-[88px] right-4 md:right-6 z-50 overflow-hidden rounded-2xl shadow-2xl
              w-[calc(100vw-32px)] h-[calc(100vh-100px)]
              md:w-[400px] md:h-[600px]
              max-md:bottom-0 max-md:right-0 max-md:w-full max-md:h-full max-md:rounded-none"
          >
            <Chatbot
              newThreadID={newThreadID}
              setThreadID={setThreadID}
              toggleChatbot={toggleChatbot}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chatbot Toggle Button — hidden on mobile when chat is open (header has its own close button) */}
      <div className={`fixed bottom-4 right-4 md:right-6 z-50 ${newThreadID ? "max-md:hidden" : ""}`}>
        <AnimatePresence>
          {showTooltip && (
            <motion.div
              key="chat-tooltip"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.25 }}
              className="absolute -top-10 right-0 flex flex-col items-end pointer-events-none"
            >
              <div className="px-3 py-1.5 rounded-lg text-indira_text text-xs font-indira_font whitespace-nowrap border border-indira_border bg-white shadow-sm">
                Chat with us!
              </div>
              <div className="mr-5 w-0 h-0 border-l-[5px] border-r-[5px] border-t-[5px] border-l-transparent border-r-transparent border-t-white" />
            </motion.div>
          )}
        </AnimatePresence>
        <motion.button
          onClick={toggleChatbot}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="w-14 h-14 rounded-full cursor-pointer flex items-center justify-center shadow-lg bg-gradient-to-br from-indira_light_red to-indira_dark_red hover:from-indira_hover_red hover:to-indira_hover_red transition-colors"
        >
          {newThreadID ? <CloseIcon /> : <ChatIcon />}
        </motion.button>
      </div>
    </div>
  );
};

export default ChatbotWidget;
