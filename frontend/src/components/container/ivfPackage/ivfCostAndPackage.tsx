import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
  type: "user" | "bot";
  content: string;
  contentType?: string;
}

interface IVFCostAndPackageProps {
  selectedLang: string;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  setThreadID: React.Dispatch<React.SetStateAction<string>>;
  setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
  newThreadID?: string;
}

const IVFCostAndPackage: React.FC<IVFCostAndPackageProps> = ({
  selectedLang,
  setMessages,
  setTyping,
  setThreadID,
  setSelectedOption,
  setshowoptions,
  newThreadID = "none",
  
}) => {
  const { ws } = useWebSocket();
  const hasSentInitial = useRef(false);

  const messagesByLanguage: Record<string, string> = {
    English: "How much does IVF cycle cost?",
    Русский: "Сколько стоит цикл ЭКО?",
  };

  const { createNewThread } = useThreads();

  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);
  useEffect(() => {
    if (!ws || hasSentInitial.current) return;

    hasSentInitial.current = true;
    setshowoptions(false);

    const getInitialMessage = (lang: string): string => {
      return messagesByLanguage[lang] || messagesByLanguage["English"];
    };

    const initialMessage = getInitialMessage(selectedLang);
    setSelectedOption("");

    // Add initial message only once
    setMessages((prev) => {
      // const alreadyExists = prev.some(
      //   (msg) => msg.content === initialMessage && msg.type === "user"
      // );
      // if (!alreadyExists) {
        return [...prev, { type: "user", content: initialMessage }];
      // }
      // return prev;
    });

    let active = true;

    const init = async () => {
      let thread_id: string;

      if (newThreadID === "none") {
        const newThread = await createNewThread(selectedLang);
        setThreadID(newThread._id);
        thread_id = newThread._id;
      } else {
        thread_id = newThreadID;
      }

      const sendInitialMessage = () => {
        setTyping(true);
        ws.send(
          JSON.stringify({
            type: "message",
            message:messagesByLanguage[selectedLang] || messagesByLanguage["English"],
            thread_id: thread_id,
            subtype: "cost_and_package",
            isflow: "confirm",
          })
        );
      };

      if (ws.readyState === WebSocket.OPEN) {
        sendInitialMessage();
      } else {
        ws.addEventListener("open", sendInitialMessage, { once: true });
      }
    };

    init();

  }, [ws, selectedLang]);
  return <></>;
};

export default IVFCostAndPackage;
