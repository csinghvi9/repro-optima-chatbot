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
    हिन्दी: "आईवीएफ चक्र की लागत कितनी है?",
    मराठी: "आयव्हीएफ सायकलचा खर्च किती आहे?",
    ગુજરાતી:"આઈવીએફ સાયકલ કેટલી કિંમત છે?",
    ಕನ್ನಡ:"ಐವಿಎಫ್ ಚಕ್ರದ ವೆಚ್ಚ ಎಷ್ಟು?",
    தமிழ்:"ஐவிஎப் சுழற்சியின் செலவு எவ்வளவு?",
    తెలుగు:"ఐవీఎఫ్ సైకిల్ ఖర్చు ఎంత?",
    বাংলা:"আইভিএফ চক্রের খরচ কত?",
    ਪੰਜਾਬੀ:"ਆਈਵੀਆਫ ਸਾਈਕਲ ਦੀ ਕੀਮਤ ਕਿੰਨੀ ਹੈ?",
    অসমীয়া:"আইভিএফ চক্রৰ খৰচ কিমান?",
    ଓଡ଼ିଆ:"ଆଇଭିଏଫ ଚକ୍ରର ଖର୍ଚ୍ଚ କେତେ?"
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
