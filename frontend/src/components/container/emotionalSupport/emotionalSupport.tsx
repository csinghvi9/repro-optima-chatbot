import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
  type: "user" | "bot";
  content: string;
  contentType?: string;
}

interface EmotionalSupportProps {
  selectedLang: string;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  setThreadID: React.Dispatch<React.SetStateAction<string>>;
  newThreadID: string;
  setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
}

const EmotionalSupport: React.FC<EmotionalSupportProps> = ({
  selectedLang,
  setMessages,
  setTyping,
  setThreadID,
  newThreadID,
  setSelectedOption,
  setshowoptions
}) => {
  const { ws } = useWebSocket();
  const hasSentInitial = useRef(false);

  const messagesByLanguage: Record<string, string> = {
    English: "I'm really nervous about the procedures",
    Русский: "Я очень переживаю по поводу процедур",
    Filipino: "Kinakabahan ako tungkol sa mga proseso",
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
      // let thread_id: string;

      // if (newThreadID === "none") {
      //   const newThread = await createNewThread(selectedLang);
      //   setThreadID(newThread._id);
      //   thread_id = newThread._id;
      // } else {
      //   thread_id = newThreadID;
      // }

      const sendInitialMessage = () => {
        setTyping(true);
        ws.send(
          JSON.stringify({
            type: "message",
            message:messagesByLanguage[selectedLang] || messagesByLanguage["English"],
            thread_id: newThreadID,
            subtype: "emotional_support",
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

    const handleMessage = (event: MessageEvent) => {
      if (!active) return;
      const data = JSON.parse(event.data);
      if (data.text) {
        setMessages((prev) => {
          if (prev.length === 0) {
            return [
              ...prev,
              { type: "bot" as const, content: data.text, contentType: data.contentType },
            ];
          }

          const lastMessage = prev[prev.length - 1];
          const newContent = data.text;

          const getHeading = (val: any) => {
            if (typeof val === "object" && val !== null && "heading" in val) {
              return val.heading;
            }
            return val;
          };

          if (
            lastMessage.type === "bot" &&
            getHeading(lastMessage.content) === getHeading(newContent)
          ) {
            return prev; // ✅ skip agar heading same hai
          }

          return [
            ...prev,
            { type: "bot" as const, content: newContent, contentType: data.contentType },
          ];
        }); 
        setTyping(false);
      }
    };

    // ws.addEventListener("message", handleMessage);

    // // Cleanup
    // return () => {
    //   active = false;
    //   ws.removeEventListener("message", handleMessage);
    // };
  }, [ws, selectedLang]);
  return <></>;
};

export default EmotionalSupport;
