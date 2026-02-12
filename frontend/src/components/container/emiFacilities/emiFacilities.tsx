import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
    type: "user" | "bot";
    content: string;
    contentType?: string;
}

interface EMIFacilitiesProps {
    selectedLang: string;
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    setTyping: React.Dispatch<React.SetStateAction<boolean>>;
    setThreadID: React.Dispatch<React.SetStateAction<string>>;
    newThreadID: string;
    setSelectedOption:React.Dispatch<React.SetStateAction<string>>
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
}

const EMIFacilities: React.FC<EMIFacilitiesProps> = ({
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
        English: "I would like to know more about the EMI facility offered by IVF.",
        हिन्दी: "मैं आईवीएफ द्वारा प्रदान की जाने वाली ईएमआई सुविधा के बारे में और जानना चाहता हूँ।",
        मराठी: "आयव्हीएफकडून दिल्या जाणाऱ्या ईएमआय सुविधेबद्दल मला अधिक माहिती हवी आहे.",
        ગુજરાતી: "મને આઈવીએફ દ્વારા આપવામાં આવતી EMI સુવિધા વિશે વધુ જાણવું છે.",
        ಕನ್ನಡ: "ಐವಿಎಫ್ ನೀಡುವ EMI ಸೌಲಭ್ಯ ಕುರಿತು ಇನ್ನಷ್ಟು ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೇನೆ.",
        தமிழ்: "ஐவிஎஃப் வழங்கும் EMI வசதி பற்றி மேலும் தெரிந்து கொள்ள விரும்புகிறேன்.",
        తెలుగు: "ఐవీఎఫ్ అందించే EMI సౌకర్యం గురించి మరింత తెలుసుకోవాలనుకుంటున్నాను.",
        বাংলা: "আইভিএফ প্রদত্ত ইএমআই সুবিধা সম্পর্কে আরও জানতে চাই।",
        ਪੰਜਾਬੀ: "ਮੈਂ ਆਈਵੀਐਫ ਵੱਲੋਂ ਦਿੱਤੀ ਜਾਣ ਵਾਲੀ ਈਐਮਆਈ ਸੁਵਿਧਾ ਬਾਰੇ ਹੋਰ ਜਾਣਕਾਰੀ ਲੈਣਾ ਚਾਹੁੰਦਾ/ਚਾਹੁੰਦੀ ਹਾਂ।",
        অসমীয়া: "আইভিএফৰ দ্বাৰা প্ৰদান কৰা ইএমআই সুবিধাৰ বিষয়ে অধিক জানিব বিচাৰোঁ।",
        ଓଡ଼ିଆ: "ଆଇଭିଏଫ୍ ପକ୍ଷରୁ ପ୍ରଦାନ କରାଯାଉଥିବା EMI ସୁବିଧା ବିଷୟରେ ଅଧିକ ଜାଣିବାକୁ ଚାହୁଁଛି।"
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
                        subtype: "loan_and_emi",
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

export default EMIFacilities;
