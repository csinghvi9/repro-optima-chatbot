import React, { useState } from "react";
import { useWebSocket } from '@/app/WebSocketContext';
import LanguageSelection from "@/components/ui/languageSelection";
import useThreads from '@/components/threads/threads.hook'


interface LanguageChangeProps {
  onSelect: (lang: string) => void;
  selectedLang?: string;
  newThreadID: string;
  setTyping?: React.Dispatch<React.SetStateAction<boolean>>;
}

const LanguageChange: React.FC<LanguageChangeProps> = ({ onSelect, selectedLang, newThreadID,setTyping}) => {
    const { sendMessage, isConnected } = useWebSocket() as {
        sendMessage: (message: any) => void;
        isConnected: boolean;
    };
    const { changeLanguage } = useThreads();
      const languages: string[] = [
    "English",
    "Русский",
  ];
    const handleSend = (formatted: string) => {
        if (formatted.trim()) {

            if (isConnected) {
                sendMessage({ type: "message", thread_id: newThreadID, message: formatted, subtype: "language_change", isflow: "not confirm" });
                if(setTyping){
        setTyping(true);}
            } else {
                console.error("WebSocket not connected");
            }
        }
    };
      const handleChangeLanguage = async (lang: string) => {
       onSelect(lang)
    };
    return (
    <div className="border border-indira_hello_border bg-white px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] flex flex-col gap-2 max-w-[80%] h-[212px]">
      <p className="text-[12px] text-indira_text">
        Please select your preferred Language
      </p>

      <div className="overflow-y-auto customScrollbar flex flex-col  gap-2 focus:outline-none">
        {languages.map((lang) => (
          <div
            key={lang}
            onClick={() => {
                handleChangeLanguage(lang);
                handleSend(lang);
                }}
            className={`px-3 py-1 rounded-full text-[12px] font-indira_font cursor-pointer text-center w-[90%] ${
              lang === selectedLang
                ? "bg-gradient-to-br from-indira_light_red to-indira_dark_red text-white"
                : "bg-red-50 text-indira_dark_red border border-red-200"
            }`}
          >
            {lang}
          </div>
        ))}
      </div>
    </div>
        
    );

};

export default LanguageChange;
