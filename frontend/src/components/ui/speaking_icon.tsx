import React from "react";

export default function MicListeningIcon() {
  return (
    <div className="w-[20px] h-[20px] cursor-pointer bg-[#FAEAED] rounded-full flex items-center justify-center overflow-hidden">
      <div className="flex gap-[2px] items-end h-[14px]">
        <span className="w-[2px] h-[10px] bg-[#CE3149] animate-bar1 rounded-full"></span>
        <span className="w-[2px] h-[10px] bg-[#CE3149] animate-bar2 rounded-full"></span>
        <span className="w-[2px] h-[10px] bg-[#CE3149] animate-bar3 rounded-full"></span>
        <span className="w-[2px] h-[10px] bg-[#CE3149] animate-bar4 rounded-full"></span>
        <span className="w-[2px] h-[10px] bg-[#CE3149] animate-bar5 rounded-full"></span>
      </div>
    </div>
  );
}