"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import Chatbot from "@/components/container/home_page/bot_ui";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";
import Typing from "@/components/ui/typing";
import { motion, AnimatePresence } from "framer-motion";

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

  // useEffect(() => {
  //   const fetchGuestToken = async () => {
  //     try {
  //       const token = sessionStorage.getItem("guest_token");

  //       if (!token || isTokenExpired(token)) {
  //         const response = await axios.get<{
  //           token?: { access_token?: string };
  //         }>(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/guest_token`);

  //         const access_token = response.data?.token?.access_token;

  //         if (access_token) {
  //           sessionStorage.setItem("guest_token", access_token);
  //           const token = sessionStorage.getItem("guest_token");
  //           if (token) {
  //             setUpWebSocket(token);
  //             const newThread = await createNewThread("English");
  //             setThreadID(newThread._id);
  //           } else {
  //             console.error("❌ No token found in session storage");
  //           }
  //         }
  //       } else {
  //         if (token) {
  //           setUpWebSocket(token);
  //           const newThread = await createNewThread("English");
  //           setThreadID(newThread._id);
  //         } else {
  //           console.error("❌ No token found in session storage");
  //         }
  //       }
  //     } catch (error) {
  //       console.error("Error fetching guest token:", error);
  //     }
  //   };

  //   if (isChatbotOpen) {
  //     fetchGuestToken();
  //   }
  // }, [isChatbotOpen]);
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

      // ✅ token dead => close bot & reset
      if (!token || isTokenExpired(token)) {
        disconnectWebSocket();
        sessionStorage.removeItem("guest_token");
        setThreadID(undefined);
        setIsChatbotOpen(false);
        window.parent.postMessage({ type: "CHATBOT_CLOSE" }, "*");
        return;
      }

      // ✅ token ok => reconnect
      setUpWebSocket(token);
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [isChatbotOpen, disconnectWebSocket, setUpWebSocket]);

  const showTooltip = !isChatbotOpen && !isLoadingChatbot;

  return (
    <>
      {/* Chatbot UI Popup */}
      <AnimatePresence>
        {newThreadID && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 400, opacity: 1 }} // adjust height as per your chatbot
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
            className="fixed bottom-6 right-6 z-50 overflow-hidden rounded-lg shadow-lg bg-white"
          >
            <Chatbot
              newThreadID={newThreadID}
              setThreadID={setThreadID}
              toggleChatbot={toggleChatbot}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* {isLoadingChatbot && (
        <div className="fixed bottom-21 right-4 bg-white p-4 rounded flex flex-row shadow text-indira_text bg-gradient-to-r from-indra_yellow to-indira_blue">
          <span className="pt-3">Connecting</span>
          <Typing />
        </div>
      )} */}

      {/* Chatbot Button Container */}
      <div className="fixed bottom-0 right-4 md:right-12 z-10 w-[60px] h-[60px]">
        <AnimatePresence>
          {showTooltip && (
            <motion.div
              key="chat-tooltip"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.25 }}
              className="absolute -top-10 md:-top-10 right-0 flex flex-col items-end pointer-events-none"
            >
              <div className="px-3 py-2 rounded-lg  text-indira_text text-xs font-indira_font whitespace-nowrap border border-indira_border bg-indira_hello_border">
                Chat with us!
              </div>
              <div className="mr-4 w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px] border-l-transparent border-r-transparent border-t-indira_border" />
            </motion.div>
          )}
        </AnimatePresence>
        {!newThreadID ? (
          <button
            onClick={toggleChatbot}
            className="w-full h-full cursor-pointer"
          >
            <img
              src="/bot_website_icon.png"
              alt="bot"
              className="w-full h-full object-cover rounded-full"
            />
          </button>
        ) : (
          <button
            onClick={toggleChatbot}
            className="w-full h-full cursor-pointer hidden md:inline-block"
          >
            <div
              className="w-full h-full rounded-[60px] bg-[#FAEAED] flex items-center justify-center "
              style={{
                border: "3px solid transparent",
                borderRadius: "60px",
                backgroundOrigin: "border-box",
                backgroundClip: "padding-box, border-box",
                backgroundImage:
                  "linear-gradient(#FAEAED, #FAEAED), linear-gradient(178.04deg, #CA5D62 1.65%, #F8CFD1 95.71%)",
              }}
            >
              <img src="./dropdown_arrow.svg" />
            </div>
          </button>
        )}
      </div>
    </>
  );
};

export default ChatbotWidget;
