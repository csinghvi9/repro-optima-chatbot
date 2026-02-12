import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
  type: "bot" | "user";
  content: string;
  contentType?: string;
}

interface IVFSuccessCalculatorProps {
  selectedLang: string;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  setThreadID: React.Dispatch<React.SetStateAction<string | undefined>>;
  setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
  newThreadID: string;
}

const IVFSuccessCalculator: React.FC<IVFSuccessCalculatorProps> = ({
  selectedLang,
  setMessages,
  setTyping,
  setThreadID,
  setSelectedOption,
  setshowoptions,
  newThreadID
}) => {
  const { ws } = useWebSocket();
  const { createNewThread } = useThreads();

  // ✅ guard to prevent duplicate initial send
  const hasInitialized = useRef(false);

  const messagesByLanguage: Record<string, string> = {
    English: "I want to know my chances for a successful IVF",
    Русский: "Я хочу узнать мои шансы на успешное ЭКО",
  };

  // Prevent body scroll on small screens
  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  useEffect(() => {
    if (!ws || hasInitialized.current) return; // ✅ don't re-run

    hasInitialized.current = true; // mark as initialized
    setshowoptions(false);
    const handleInitial = async () => {
      const initialMessage =
        messagesByLanguage[selectedLang] || messagesByLanguage["English"];
        setSelectedOption("");

      // add user message once
      setMessages((prev) => {
        // const alreadyExists = prev.some(
        //   (msg) => msg.content === initialMessage && msg.type === "user"
        // );
        // if (!alreadyExists) {
          return [...prev, { type: "user", content: initialMessage }];
        
        // return prev;
      });

      // create a new thread
      // const newThread = await createNewThread(selectedLang);
      // setThreadID(newThread._id);

      const sendInitialMessage = () => {
        setTyping(true);
        ws.send(
          JSON.stringify({
            type: "message",
            message:messagesByLanguage[selectedLang] || messagesByLanguage["English"],
            thread_id: newThreadID,
            subtype: "ivf_success_calculator",
            isflow: "confirm",
          })
        );
      };

      if (ws.readyState === WebSocket.OPEN) {
        sendInitialMessage();
      } else {
        ws.addEventListener("open", sendInitialMessage, { once: true });
      }

      // handle bot messages
      const handleMessage = (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        if (data.text) {
          setMessages((prev) => [
            ...prev,
            { type: "bot", content: data.text, contentType: data.contentType },
          ]);
          setTyping(false);
        }
      };

      // ws.addEventListener("message", handleMessage);

      // return () => {
      //   ws.removeEventListener("message", handleMessage);
      // };
    };

    handleInitial();
  }, [ws, selectedLang, setMessages, setThreadID, setTyping, createNewThread]);

  return <></>;
};

export default IVFSuccessCalculator;
