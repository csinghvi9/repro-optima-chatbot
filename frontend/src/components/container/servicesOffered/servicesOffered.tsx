import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
    type: "user" | "bot";
    content: string;
    contentType?: string;
}

interface ServicesOfferedProps {
    selectedLang: string;
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    setTyping: React.Dispatch<React.SetStateAction<boolean>>;
    setThreadID: React.Dispatch<React.SetStateAction<string>>;
    newThreadID: string;
    setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
}

const ServicesOffered: React.FC<ServicesOfferedProps> = ({
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
        English: "What services does Indira IVF offer ?",
        हिन्दी: "इंदिरा आईवीएफ कौन-कौन सी सेवाएं प्रदान करता है?",
        मराठी: "इंदिरा आयव्हीएफ कोणत्या सेवा पुरवते?",
        ગુજરાતી: "ઇંદિરા આઈવીએફ કયા કયા સેવાઓ પ્રદાન કરે છે?",
        ಕನ್ನಡ: "ಇಂದಿರಾ ಐವಿಎಫ್ ಯಾವ ಯಾವ ಸೇವೆಗಳನ್ನು ಒದಗಿಸುತ್ತದೆ?",
        தமிழ்: "இந்திரா ஐவிஎஃப் எந்த சேவைகளை வழங்குகிறது?",
        తెలుగు: "ఇందిరా ఐవీఎఫ్ ఏఏ సేవలను అందిస్తుంది?",
        বাংলা: "ইন্দিরা আইভিএফ কোন কোন সেবা প্রদান করে?",
        ਪੰਜਾਬੀ: "ਇੰਦਿਰਾ ਆਈਵੀਐਫ ਕਿਹੜੀਆਂ ਸੇਵਾਵਾਂ ਪ੍ਰਦਾਨ ਕਰਦੀ ਹੈ?",
        অসমীয়া: "ইন্দিৰা আইভিএফ কোন কোন সেৱা আগবঢ়ায়?",
        ଓଡ଼ିଆ: "ଇନ୍ଦିରା ଆଇଭିଏଫ୍ କେଉଁ କେଉଁ ସେବା ପ୍ରଦାନ କରେ?"
    };


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
            //     (msg) => msg.content === initialMessage && msg.type === "user"
            // );
            // if (!alreadyExists) {
                return [...prev, { type: "user", content: initialMessage }];
            // }
            // return prev;
        });

        let active = true;

        const init = async () => {

            const sendInitialMessage = () => {
                setTyping(true);
                ws.send(
                    JSON.stringify({
                        type: "message",
                        message:messagesByLanguage[selectedLang] || messagesByLanguage["English"],
                        thread_id: newThreadID,
                        subtype: "add_on_service",
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

        // ws.addEventListener("message", handleMessage);

        // // Cleanup
        // return () => {
        //   active = false;
        //   ws.removeEventListener("message", handleMessage);
        // };
    }, [ws, selectedLang]);
    return <></>;
};

export default ServicesOffered;
