import React from "react";
import { useWebSocket } from "@/app/WebSocketContext";

interface LifestyleAndPreparationsProps {
  msg: {
    heading: string;
    alcohol: string;
    Smoking: string;
    hydration: string;
    stress: string;
  };
}

const LifestyleAndPreparations: React.FC<LifestyleAndPreparationsProps> = ({
  msg,
}) => {
  return (
    <div
      className=" rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs flex flex-row h-[212px] bg-white"
      style={{
        border: "1px solid",
        borderImageSource:
          "linear-gradient(89.54deg, #D199FF 0.35%, rgba(255, 255, 255, 0.7) 99.59%)",
        borderImageSlice: 1,
      }}
    >
      {/* Left Section */}
      <div className=" w-[30%] md:w-[40%] h-full flex flex-col justify-between">
        <div className="flex items-center justify-center">
          <span className="font-bold w-[90%] text-sm md:text-base mt-4 md:ml-4 font-indira_second_font text-indira_text">
            {msg?.heading}
          </span>
        </div>
        <img src="/imgBot.svg" alt="Bot" className="w-[80%] self-center" />
      </div>

      {/* Right Section */}
      <div className="w-[70%] md:w-[60%] h-full text-indira_text grid grid-rows-4  text-xs bg-[#F9F9F9] rounded-tl-[8px] rounded-bl-[8px]">
        <div className="flex flex-col items-center justify-center gap-1 text-center pt-1 ">
          <img src="/alcohol.svg" alt="Avoid Alcohol" className="w-[50%] h-[30%]" />
          <span className="w-[100%] break-words">{msg?.alcohol}</span>
        </div>
        <div className="flex flex-col items-center justify-center gap-1 text-center ">
          <img src="/smoking.svg" alt="Avoid Smoking" className="w-[50%] h-[30%]" />
          <span className="w-[100%] break-words">{msg?.Smoking}</span>
        </div>
        <div className="flex flex-col items-center justify-center gap-1 text-center ">
          <img src="/water.svg" alt="Stay Hydrated" className="w-[50%] h-[30%]" />
          <span className="w-[100%] break-words">{msg?.hydration}</span>
        </div>
        <div className="flex flex-col items-center justify-center gap-1 text-center ">
          <img src="/stress.svg" alt="Avoid Stress" className="w-[50%] h-[30%]" />
          <span className="w-[100%] break-words">{msg?.stress}</span>
        </div>
      </div>
    </div>
  );
};

export default LifestyleAndPreparations;
