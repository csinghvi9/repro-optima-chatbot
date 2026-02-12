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
    हिन्दी: "मैं सफल आईवीएफ की अपनी संभावनाओं के बारे में जानना चाहता हूँ",
    मराठी: "मला यशस्वी आयव्हीएफ होण्याची माझी शक्यता जाणून घ्यायची आहे.",
    ગુજરાતી: "હું સફળ આઇવીએફની મારી શક્યતાઓ જાણવા માંગું છું",
    ಕನ್ನಡ:"ಸಫಲ ಐವಿಎಫ್ ಗೆ ನನ್ನ ಅವಕಾಶಗಳನ್ನು ನಾನು ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೇನೆ",
    தமிழ்: "நான் வெற்றிகரமான ஐவிஎப் வாய்ப்புகளை தெரிந்து கொள்ள விரும்புகிறேன்",
    తెలుగు:"నాకు విజయవంతమైన ఐవీఎఫ్ కోసం నా అవకాశాలు తెలుసుకోవాలనుకుంటున్నాను",
    বাংলা:"আমি সফল আইভিএফের জন্য আমার সম্ভাবনা জানতে চাই",
    ਪੰਜਾਬੀ:"ਮੈਂ ਜਾਣਨਾ ਚਾਹੁੰਦਾ ਹਾਂ ਕਿ ਮੇਰੇ ਸਫਲ ਆਈਵੀਆਫ ਲਈ ਮੌਕੇ ਕੀ ਹਨ",
    অসমীয়া:"মই সফল আইভিএফৰ বাবে মোৰ সম্ভাৱনাসমূহ জানিব বিচাৰো",
    ଓଡ଼ିଆ:"ମୁଁ ସଫଳ ଆଇଭିଏଫ ପାଇଁ ମୋର ସମ୍ଭାବନାଗୁଡ଼ିକ ଜାଣିବାକୁ ଚାହୁଁଛି"
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
