import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
  type: "user" | "bot";
  content: string;
  contentType?: string;
}

interface SuccessRateProps {
  selectedLang: string;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  setThreadID: React.Dispatch<React.SetStateAction<string>>;
  setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
  newThreadID?: string;
}

const SuccessRate: React.FC<SuccessRateProps> = ({
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
    English: "What is the success rate at IVF?",
    हिन्दी: "आईवीएफ में सफलता दर क्या है?",
    मराठी: "आयव्हीएफमध्ये यशाचे प्रमाण किती आहे?",
    ગુજરાતી:"આઈવીએફમાં સફળતાનો દર શું છે?",
    ಕನ್ನಡ:"ಐವಿಎಫ್ ನಲ್ಲಿ ಯಶಸ್ಸಿನ ದರ ಎಷ್ಟು?",
    தமிழ்:"ஐவிஎபில் வெற்றிகரமான வீதம் என்ன?",
    తెలుగు:"ఐవీఎఫ్‌లో విజయాల రేటు ఎంత?",
    বাংলা:"আইভিএফে সফলতার হার কত?",
    ਪੰਜਾਬੀ:"ਆਈਵੀਆਫ ਵਿੱਚ ਸਫਲਤਾ ਦਰ ਕੀ ਹੈ?",
    অসমীয়া:"আইভিএফত সফলতাৰ হাৰ কিমান?",
    ଓଡ଼ିଆ:"ଆଇଭିଏଫରେ ସଫଳତା ହାର କେତେ?"
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
    setSelectedOption("");
    const initialMessage = getInitialMessage(selectedLang);

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
            subtype: "success_rate",
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

export default SuccessRate;
