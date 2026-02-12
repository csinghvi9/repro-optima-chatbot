import React from "react";

interface HelloMessageBoxProps {
  msg?: string;
}
const HelloMessage: React.FC<HelloMessageBoxProps> = ({msg}) => {
  return (
    <div className=" w-[80%] ">
      {/* SVG on top */}
      <div className="relative left-[22px] w-[95px] h-[95px] z-0">
        <img src="/bot_hi_icon.png" alt="bot" className="w-full h-full" />
      </div>

      {/* Message bubble */}
      <div className="relative -top-[20px] flex items-start gap-2 w-[230px] h-[56px] z-10 pl-2">
        {/* Icon Container */}
        <div className="w-[36px] h-[36px]">
          {/* Optional icon here */}
          {/* <img src="/bot_icon.svg" alt="bot icon" className="w-[26px] h-[30px]" /> */}
        </div>

        {/* Chat Bubble */}
        <div
          className="max-w-[85%] border border-indira_hello_border 
                     bg-white pl-[10px] py-[10px] rounded-tl-[10px] rounded-tr-[10px] 
                     rounded-br-[10px] rounded-bl-[4px] flex items-center"
        >
          <p className="text-[12px] font-normal font-indira_font leading-[150%] tracking-[0%] text-indira_text">
           {msg || "Hello 👋 I’m here to help you with all your queries and tasks"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default HelloMessage;
