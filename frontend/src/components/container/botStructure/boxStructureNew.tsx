"use client";
import React, { useState, useEffect, ReactNode, useRef } from "react";
import { useWebSocket } from "@/app/WebSocketContext";
import MicListeningIcon from "@/components/ui/speaking_icon";
import useThreads from "@/components/threads/threads.hook";
// import { pipeline } from "@xenova/transformers";
import { options } from "@/components/constants/options";
import * as sdk from "microsoft-cognitiveservices-speech-sdk";
import { IoMdClose } from "react-icons/io";


type Message = {
  type: "bot" | "user";
  content: any;
  contentType?:string;
};

type BotStructureProps = {
  children: ReactNode;
  selectedLang?: string;
  newThreadID: string;
  setSelectedLang: (lang: string) => void;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  setshowoptions: React.Dispatch<React.SetStateAction<boolean>>;
  setThreadID: React.Dispatch<React.SetStateAction<any>>;
  isunderdevelopementsection: React.Dispatch<React.SetStateAction<boolean>>;
  setSelectedOption: React.Dispatch<React.SetStateAction<string>>;
  translatedOptions: string[];
  initialOptions: boolean;
  setinitialOptions: React.Dispatch<React.SetStateAction<boolean>>;
  toggleChatbot: () => void;
};

export function isIOS() {
  if (typeof window !== "undefined" && typeof navigator !== "undefined") {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
  }
  return false;
}
export function isIPad() {
  if (typeof navigator !== "undefined") {
    const ua = navigator.userAgent || navigator.vendor || (window as any).opera;

    // Old iPads
    if (/iPad/.test(ua)) return true;

    // New iPads (iPadOS 13+ reports as Macintosh)
    if (
      /Macintosh/.test(ua) &&
      typeof navigator.maxTouchPoints === "number" &&
      navigator.maxTouchPoints > 2
    ) {
      return true;
    }
  }
  return false;
}

export default function BotStructureNew({
  children,
  selectedLang,
  setSelectedLang,
  newThreadID,
  messages,
  setMessages,
  setTyping,
  setshowoptions,
  setThreadID,
  isunderdevelopementsection,
  setSelectedOption,
  translatedOptions,
  initialOptions,
  setinitialOptions,
  toggleChatbot,
}: BotStructureProps) {
  const [message, setMessage] = useState("");
  const [isIOSDevice, setIsIOSDevice] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  //const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [micStatus, setMicStatus] = useState<
    "idle" | "listening" | "speaking" | "loading"
  >("idle");
  const recognitionRef = useRef<any>(null);
  const { ws, sendMessage, isConnected, setUpWebSocket } = useWebSocket() as {
    ws: WebSocket | null;
    sendMessage: (message: any) => void;
    isConnected: boolean;
    setUpWebSocket: (token: string) => void;
  };
  const { changeLanguage } = useThreads();
  const { createNewThread } = useThreads();
  let active = true;
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [loading, setLoading] = useState(false);
  const [isMobile, setISMobile] = useState(false);
  const isActuallyMobile =
    window.innerWidth < 768 && window.innerHeight > window.innerWidth;

  // useEffect(() => {
  //   setIsIOSDevice(isIOS());
  //   const handleResize = () => {
  //     setISMobile(window.innerWidth < 768)
  //   }
  //   handleResize()
  // }, []);

  // useEffect(() => {
  //     if (window.innerWidth < 768 && !isIPad()) {
  //         document.body.style.overflow = "hidden";
  //     }
  //     return () => {
  //         document.body.style.overflow = "auto";
  //     };
  // }, []);
  // useEffect(() => {
  //   // only when tall portrait (real phone-like)
  //   if (isActuallyMobile) {
  //     document.body.style.overflow = "hidden";
  //     setISMobile(true)
  //     // document.body.style.overflowX = "hidden"; // mobile phones
  //   } else {
  //     document.body.style.overflow = "auto";
  //     setISMobile(false)
  //     // tablets, iPads, desktops
  //   }
  // }, []);
  useEffect(() => {
    const handleResize = () => {
      const isMobileCheck =
        window.innerWidth < 768 //&& window.innerHeight >= window.innerWidth;
      setISMobile(isMobileCheck);

      // Optional body overflow logic
      document.body.style.overflow = isMobileCheck ? "hidden" : "auto";
    };

    // Fire immediately
    handleResize();

    // Listen on window resize
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);
  useEffect(() => {
    if (!ws) return;
    if (!isConnected) return;

    let active = true;
    const handleMessage = (event: MessageEvent) => {
      if (!active) return;
      const data = JSON.parse(event.data);
      if (data.text) {
        setMessages((prev) => {
          if (prev.length === 0) {
            return [
              ...prev,
              {
                type: "bot" as const,
                content: data.text,
                contentType: data.contentType,
              },
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
            return prev; // skip if heading same
          }

          return [
            ...prev,
            {
              type: "bot" as const,
              content: newContent,
              contentType: data.contentType,
            },
          ];
        });
        setTyping(false);
      }
    };

    ws.addEventListener("message", handleMessage);

    return () => {
      active = false;
      ws.removeEventListener("message", handleMessage);
    };
  }, [ws]);
  const langCodeMap: Record<string, string> = {
    English: "en-US", // English
    Русский: "ru-RU", // Russian
  };
  const handleMicClick = async () => {
    if (micStatus !== "listening") {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

        const audioConfig = sdk.AudioConfig.fromDefaultMicrophoneInput();
        const speechConfig = sdk.SpeechConfig.fromSubscription(
          process.env.NEXT_PUBLIC_AZURE_SPEECH_KEY!,
          process.env.NEXT_PUBLIC_AZURE_SPEECH_REGION!
        );

        // ✅ Ensure valid BCP-47 code

        let lang: string;

        if (selectedLang){
        lang = langCodeMap[selectedLang];
        }
        else{
          lang= "en-IN";
        }

        speechConfig.speechRecognitionLanguage = lang;

        const recognizer = new sdk.SpeechRecognizer(speechConfig, audioConfig);

        setMicStatus("listening");
        setMessage("");

        recognizer.recognizeOnceAsync(
          (result) => {
            if (result.reason === sdk.ResultReason.RecognizedSpeech) {
              setMicStatus("speaking");
              setMessage(result.text);
            } else {
              console.error("Speech recognition failed:", result.errorDetails);
            }
            recognizer.close();
            setTimeout(() => {
              setMicStatus("idle");
            }, 1000);
          },
          (err) => {
            console.error("Speech SDK error:", err);
            recognizer.close();
            setTimeout(() => {
              setMicStatus("idle");
            }, 1000);
          }
        );
      } catch (err) {
        console.error("Mic access error:", err);
      }
    } else {
      setMicStatus("idle");
    }
  };
  // const handleMicClick = () => {
  //     if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
  //         alert("Speech recognition is not supported in this browser.");
  //         return;
  //     }

  //     const SpeechRecognition =
  //         (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

  //     // 🔴 If recognition already exists, stop it before creating new
  //     if (recognitionRef.current) {
  //         recognitionRef.current.stop();
  //         recognitionRef.current = null;
  //     }

  //     const recognition = new SpeechRecognition();
  //     recognitionRef.current = recognition;

  //     recognition.lang = langCodeMap[selectedLang] || "en-IN";
  //     recognition.interimResults = true;
  //     recognition.continuous = false;

  //     recognition.onstart = () => {
  //         setMicStatus("listening");
  //         setMessage("");
  //     };

  //     recognition.onresult = (event: any) => {
  //         let transcript = "";
  //         for (let i = event.resultIndex; i < event.results.length; i++) {
  //             transcript += event.results[i][0].transcript;
  //         }
  //         setMessage(transcript);

  //         if (transcript.trim().length > 0) {
  //             setMicStatus("speaking");
  //         }
  //     };

  //     recognition.onerror = (event: any) => {
  //         console.error("Speech recognition error:", event.error);
  //         setMicStatus("idle");
  //     };

  //     recognition.onend = () => {
  //         if (message.trim().length > 0) {
  //             setMicStatus("loading");
  //         } else {
  //             setMicStatus("idle");
  //         }
  //         recognitionRef.current = null;
  //     };

  //     recognition.start();
  // };
  // const handleMicClick = async () => {
  //   if (isRecording) {
  //     // Already recording, ignore click
  //     return;
  //   }

  //   setMicStatus("listening");

  //   try {
  //     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  //     const mediaRecorder = new MediaRecorder(stream);
  //     mediaRecorderRef.current = mediaRecorder;

  //     const chunks: BlobPart[] = [];

  //     mediaRecorder.ondataavailable = (e) => {
  //       if (e.data.size > 0) chunks.push(e.data);
  //     };

  //     mediaRecorder.onstop = async () => {
  //       // Stop all tracks to release mic
  //       stream.getTracks().forEach((track) => track.stop());

  //       const audioBlob = new Blob(chunks, { type: "audio/webm" });
  //       const formData = new FormData();
  //       formData.append("file", audioBlob, "audio.webm");
  //       formData.append("model", "whisper-1");

  //       setMicStatus("listening");

  //       try {
  //         setMicStatus("speaking");
  //         const response = await fetch(
  //           "https://api.openai.com/v1/audio/transcriptions",
  //           {
  //             method: "POST",
  //             headers: {
  //               Authorization: `Bearer ${process.env.NEXT_PUBLIC_OPENAI_API_KEY}`,
  //             },
  //             body: formData,
  //           }
  //         );

  //         const data = await response.json();

  //         const gResponse = await fetch(
  //           "https://api.openai.com/v1/chat/completions",
  //           {
  //             method: "POST",
  //             headers: {
  //               Authorization: `Bearer ${process.env.NEXT_PUBLIC_OPENAI_API_KEY}`,
  //               "Content-Type": "application/json",
  //             },
  //             body: JSON.stringify({
  //               model: "gpt-4.1-nano",
  //               messages: [
  //                 {
  //                   role: "system",
  //                   content: `You are a multilingual transliterator. Convert text into: ${selectedLang}`,
  //                 },
  //                 {
  //                   role: "user",
  //                   content: `Transliterate this text to its native script: ${data.text}`,
  //                 },
  //               ],
  //             }),
  //           }
  //         );

  //         const gData = await gResponse.json();
  //         const nativeScriptText = gData.choices[0].message.content;

  //         setMessage(nativeScriptText);
  //         setTranscript(nativeScriptText || "No text returned");
  //         setMicStatus("idle");
  //       } catch (err) {
  //         console.error("❌ Transcription error:", err);
  //         setMicStatus("idle");
  //       }

  //       setLoading(false);
  //     };

  //     mediaRecorder.start();
  //     setIsRecording(true);

  //     // --- Silence detection logic ---
  //     const audioContext = new AudioContext();
  //     const source = audioContext.createMediaStreamSource(stream);
  //     const analyser = audioContext.createAnalyser();
  //     analyser.fftSize = 2048;
  //     source.connect(analyser);

  //     const dataArray = new Uint8Array(analyser.fftSize);
  //     let silenceStart: number | null = null;
  //     const SILENCE_THRESHOLD = 10; // adjust sensitivity
  //     const SILENCE_DURATION = 1000; // 1 second of silence

  //     const checkSilence = () => {
  //       analyser.getByteTimeDomainData(dataArray);
  //       const rms = Math.sqrt(
  //         dataArray.reduce((sum, val) => sum + (val - 128) ** 2, 0) /
  //           dataArray.length
  //       );

  //       if (rms < SILENCE_THRESHOLD) {
  //         if (!silenceStart) silenceStart = Date.now();
  //         else if (Date.now() - silenceStart > SILENCE_DURATION) {
  //           mediaRecorder.stop(); // auto-stop on silence
  //           setIsRecording(false);
  //           audioContext.close();
  //           return;
  //         }
  //       } else {
  //         silenceStart = null; // reset if user is speaking
  //       }

  //       requestAnimationFrame(checkSilence);
  //     };

  //     checkSilence(); // start monitoring
  //   } catch (err) {
  //     console.error("❌ Could not start microphone:", err);
  //     setMicStatus("idle");
  //   }
  // };

  const handleSendMessage = async () => {
    if (message.trim()) {
      setMessages((prev) => [...prev, { type: "user", content: message }]);

      if (isConnected && newThreadID) {
        isunderdevelopementsection(false);
        setSelectedOption("");
        sendMessage({
          type: "message",
          thread_id: newThreadID,
          message: message,
          subtype: "",
          isflow: "not confirm",
        });
        setshowoptions(false);
        setinitialOptions(false);
        setTyping(true);
        setMessage("");
      }

      // } else if (!newThreadID) {
      //     // const token = sessionStorage.getItem("guest_token");
      //     // if (token) {
      //     //     setUpWebSocket(token);
      //     // } else {
      //     //     console.error("❌ No token found in session storage");
      //     // }
      //     if (isConnected) {
      //     const newThread = await createNewThread(selectedLang);
      //     setThreadID(newThread._id);
      //     sendMessage({ type: "message", thread_id: newThread._id, message: message, subtype: "appointment", isflow: "not confirm" });
      //     setshowoptions(false);
      //     setTyping(true);
      //     setMessage("");
      // }

      // }
      else {
        console.error("WebSocket not connected");
      }

      setInput("");
    }
  };
  const handleChangeLanguage = async (thread_id: string, lang: string) => {
    await changeLanguage(thread_id, lang);
  };

  return (
    <div className="primary-gradient flex flex-row">
      <div className="flex items-center justify-between shadow-[0px_4px_14px_0px_#0000000D] bg-white md:rounded-t-[12px] px-4 py-3">
          <div
            onClick={() => toggleChatbot()}
            className="bg-indira_language_circle rounded-full flex items-center justify-center cursor-pointer p-2"
          >
            <IoMdClose className="w-4 h-4 text-black" />
          </div>
          <p className="text-base font-semibold font-indira_font text-indira_text">
            Chat with us
          </p>
      
        <div
          onClick={() => setIsOpen(!isOpen)}
          className="bg-indira_language_circle rounded-full flex items-center justify-center cursor-pointer h-[40px] w-[40px]"
        >
          <img
            src="/language_icon.svg"
            alt="bot"
            className="h-[18.38px] w-[20.62px]"
          />
        </div>
        {isOpen && (
          <div className="absolute top-[52px] right-3 bg-white border border-indira_hello_border rounded-xl shadow-lg z-50 px-3 py-3">
            <p className="font-semibold font-indira_font text-[12px] text-indira_text mb-2">
              Change Language
            </p>
            <div className="flex flex-row gap-2">
              {[
                { label: "English", flag: "\uD83C\uDDEC\uD83C\uDDE7" },
                { label: "\u0420\u0443\u0441\u0441\u043A\u0438\u0439", flag: "\uD83C\uDDF7\uD83C\uDDFA" },
              ].map((lang, index) => (
                <div
                  key={index}
                  onClick={() => {
                    setSelectedLang(lang.label);
                    handleChangeLanguage(newThreadID, lang.label);
                    setIsOpen(false);
                  }}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[12px] cursor-pointer transition-all ${
                    lang.label === selectedLang
                      ? "bg-gradient-to-br from-indira_light_red to-indira_dark_red text-white shadow-sm"
                      : "bg-red-50 text-indira_dark_red border border-red-200 hover:bg-red-100"
                  }`}
                >
                  <span className="text-sm">{lang.flag}</span>
                  {lang.label}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="flex-1 overflow-y-auto px-4 max-md:grow space-y-4 overflow-x-hidden no-scrollbar pt-4 ">
        {children}
      </div>
      <div className="px-2">
        {!initialOptions && (
          <div className="flex overflow-x-auto gap-2 horizontalcustomScrollbar py-1">
            {translatedOptions.map((opt, i) => (
              <button
                key={i}
                className="whitespace-nowrap cursor-pointer border border-indira_dark_red text-indira_text font-indira_font text-xs px-2 py-2 rounded-full hover:text-indira_hover_text transition flex-shrink-0"
                onClick={() => {
                  setSelectedOption(opt);
                }}
              >
                {opt}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="flex items-center gap-2 px-4 py-3">
        {/*"relative bottom-[16px] left-[16px] right-4 flex items-center space-x-2">*/}
        <div className="flex items-center grow gap-2 bg-white p-2 rounded-lg border-1 border-indira_border">
          <input
            type="text"
            className={`grow bg-white px-2.5 py-1  border-indira_border rounded-[6px]  font-normal font-indira_font text-indira_text inline-block ${
              isIOSDevice ? "text-base" : "text-sm"
            } placeholder:indira_input_label_text  focus:outline-none focus:ring-0 focus:border-indira_dark_red`}
            placeholder={isListening ? "Listening..." : " Type your query here"}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          />
          <div className="h-[20.5px] w-0.5 bg-indira_divider opacity-100"></div>
          {micStatus === "speaking" ? (
            <MicListeningIcon />
          ) : (
            <img
              src={
                micStatus === "listening"
                  ? "/listening_icon.svg"
                  : micStatus === "loading"
                  ? "/loading_icon.svg"
                  : "/mic_icon.svg"
              }
              alt="mic"
              className="w-[20px] h-[20px] cursor-pointer"
              onClick={handleMicClick}
            />
          )}
        </div>
        <button
          className="flex cursor-pointer  items-center justify-center w-[40px] h-[40px] bg-gradient-to-br from-indira_light_red to-indira_dark_red hover:from-indira_hover_red hover:to-indira_hover_red rounded-[8px] top-[2px] left-[318px]"
          onClick={handleSendMessage}
        >
          <img
            src="/send_icon.svg"
            alt="bot"
            className=" top-[8px] left-[8px] w-[20px] h-[20px]"
          />
        </button>
      </div>
    </div>
  );
}
