import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
  type: "user" | "bot";
  content: string;
  contentType?: string;
}

interface ChangePhoneNumberProps {
  selectedLang?: string;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  newThreadID: string;
  setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
  ischangephonenumber:React.Dispatch<React.SetStateAction<boolean>>;
}

const ChangePhoneNumber: React.FC<ChangePhoneNumberProps> = ({
  selectedLang,
  setMessages,
  setTyping,
  newThreadID,
  setSelectedOption,
  setshowoptions,
  ischangephonenumber


}) => {
  const { ws } = useWebSocket();
  const hasSentInitial = useRef(false);


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

    setSelectedOption("");


    let active = true;

    const init = async () => {


      const sendInitialMessage = () => {
        setTyping(true);
        ischangephonenumber(false);
        ws.send(
          JSON.stringify({
            type: "message",
            thread_id: newThreadID,
            subtype: "change_phone_number",
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

    // ✅ Attach listener once
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

  }, [ws, selectedLang]);
  return <></>;
};

export default ChangePhoneNumber;
