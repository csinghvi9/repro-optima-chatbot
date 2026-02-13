import React from "react";

const BotGreetingIcon = () => (
  <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
    <circle cx="40" cy="40" r="36" fill="#CE3149" opacity="0.1"/>
    <rect x="18" y="26" width="44" height="34" rx="12" fill="#CE3149"/>
    <circle cx="32" cy="41" r="4" fill="white"/>
    <circle cx="48" cy="41" r="4" fill="white"/>
    <path d="M33 50C35.5 53 44.5 53 47 50" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    <line x1="40" y1="26" x2="40" y2="18" stroke="#CE3149" strokeWidth="3" strokeLinecap="round"/>
    <circle cx="40" cy="15" r="3.5" fill="#CE3149"/>
    <rect x="10" y="38" width="8" height="6" rx="3" fill="#CE3149"/>
    <rect x="62" y="38" width="8" height="6" rx="3" fill="#CE3149"/>
  </svg>
);

interface HelloMessageBoxProps {
  msg?: string;
}
const HelloMessage: React.FC<HelloMessageBoxProps> = ({msg}) => {
  return (
    <div className=" w-[80%] ">
      {/* Bot icon on top */}
      <div className="relative left-[22px] w-[80px] h-[80px] z-0">
        <BotGreetingIcon />
      </div>

      {/* Message bubble */}
      <div className="relative -top-[16px] flex items-start gap-2 w-[230px] z-10 pl-2">
        {/* Icon Container */}
        <div className="w-[36px] h-[36px] shrink-0" />

        {/* Chat Bubble */}
        <div
          className="max-w-[85%] border border-indira_hello_border
                     bg-white pl-[10px] py-[10px] rounded-tl-[10px] rounded-tr-[10px]
                     rounded-br-[10px] rounded-bl-[4px] flex items-center"
        >
          <p className="text-[12px] font-normal font-indira_font leading-[150%] tracking-[0%] text-indira_text">
           {msg || "Hello 👋 I'm here to help you with all your queries and tasks"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default HelloMessage;
