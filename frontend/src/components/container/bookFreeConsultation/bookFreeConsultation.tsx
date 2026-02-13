import { useEffect, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import useThreads from "@/components/threads/threads.hook";

interface Message {
  type: "user" | "bot";
  content: string;
  contentType?: string;
}

interface BookFreeConsultationProps {
  selectedLang: string;
  setMessages?: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping?: React.Dispatch<React.SetStateAction<boolean>>;
  setThreadID?: React.Dispatch<React.SetStateAction<string | undefined>>;
  newThreadID: string;
  setSelectedOption?:React.Dispatch<React.SetStateAction<string>>
  setshowoptions?: React.Dispatch<React.SetStateAction<boolean>>;
}

const BookFreeConsultation: React.FC<BookFreeConsultationProps> = ({
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
    English: "Book Free Consultation",
    Русский: "Записаться на бесплатную консультацию",
    Filipino: "Mag-book ng Libreng Konsultasyon",
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

  // useEffect(() => {
  //   if (ws && !hasSentInitial.current) {
  //     hasSentInitial.current = true;
  //     if (button ===true)
  //     {
  //       hasSentInitial.current = false;
  //       setButton(false)
  //     }

  //     const handleInitial = async () => {
  //       const getInitialMessage = (lang: string): string => {
  //         return messagesByLanguage[lang] || messagesByLanguage["English"];
  //       };

  //       const initialMessage = getInitialMessage(selectedLang);

  //       // Add initial message only once
  //       setMessages((prev) => {
  //         const alreadyExists = prev.some(
  //           (msg) => msg.content === initialMessage && msg.type === "user"
  //         );
  //         if (!alreadyExists) {
  //           return [...prev, { type: "user", content: initialMessage }];
  //         }
  //         return prev;
  //       }); 

  //       let thread_id: string;
  //       // Await createNewThread here
  //       if (newThreadID === "none")
  //       {
  //        const newThread = await createNewThread(selectedLang);
  //        setThreadID(newThread._id);
  //        thread_id = newThread._id;
  //       }
  //       else
  //       {
  //         thread_id = newThreadID;
  //       }

  //       // Send message via WebSocket
  //       const sendInitialMessage = () => {
  //         setTyping(true);
  //         ws.send(
  //           JSON.stringify({
  //             type: "message",
  //             thread_id: thread_id,
  //             subtype: "book_appointment",
  //             isflow: "confirm",
  //           })
  //         );
  //       };

  //       if (ws.readyState === WebSocket.OPEN) {
  //         sendInitialMessage();
  //       } else {
  //         ws.addEventListener("open", sendInitialMessage);
  //       }

  //       // Listen for bot response
  //       const handleMessage = (event: MessageEvent) => {
  //         const data = JSON.parse(event.data);
  //         if (data.text) {
  //           console.log("inside data.text setting message twice")
  //           setMessages((prev) => [
  //             ...prev,
  //             {
  //               type: "bot",
  //               content: data.text,
  //               contentType: data.contentType,
  //             },
  //           ]);
  //           setTyping(false);
  //         }
  //       };

  //       ws.addEventListener("message", handleMessage);

  //       // Cleanup
  //       return () => {
  //         ws.removeEventListener("message", handleMessage);
  //         ws.removeEventListener("open", sendInitialMessage);
  //       };
  //     };

  //     handleInitial();
  //   } 
  // }, [ws, selectedLang,setMessages,setThreadID]);
  useEffect(() => {
    if (!ws || hasSentInitial.current) return;

    hasSentInitial.current = true;
    if(setshowoptions){
    setshowoptions(false);
    }

    const getInitialMessage = (lang: string): string => {
      return messagesByLanguage[lang] || messagesByLanguage["English"];
    };

    const initialMessage = getInitialMessage(selectedLang);
    if (setSelectedOption){
    setSelectedOption("");}

    // Add initial message only once
    if (setMessages){
    setMessages((prev) => {
      // const alreadyExists = prev.some(
      //   (msg) => msg.content === initialMessage && msg.type === "user"
      // );
      // if (!alreadyExists) {
        return [...prev, { type: "user", content: initialMessage }];
      // }
      // return prev;
    })};

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
        if(setTyping){
        setTyping(true);}
        ws.send(
          JSON.stringify({
            type: "message",
            message:messagesByLanguage[selectedLang] || messagesByLanguage["English"],
            thread_id: newThreadID,
            subtype: "book_appointment",
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
        if (setMessages){
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
        if(setTyping){
        setTyping(true);}
      }}
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

export default BookFreeConsultation;
