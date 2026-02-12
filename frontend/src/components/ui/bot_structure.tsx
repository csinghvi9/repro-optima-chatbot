import React, { ReactNode } from "react";



type BotStructureProps = {
  children: ReactNode;
  setBotUI:React.Dispatch<React.SetStateAction<boolean>>;
};

export default function BotStructure({
  children,
  setBotUI
}: BotStructureProps) {

  return (
<div className="w-full h-full flex flex-col bg-gradient-to-r from-[#fafee9] to-[#ecfbfc]">
      <div className="flex items-center justify-between shadow-[0px_4px_14px_0px_#0000000D]  bg-white md:rounded-t-[12px] px-4 py-3">
        <p className="text-base font-semibold font-indira_font text-indira_text">
          Chat with Indira Bot
        </p>
         <div className="">
          <button
            onClick={() => setBotUI(false)}
            className="absolute right-5 top-4 text-gray-500 hover:text-gray-700 cursor-pointer"
          >
            <img src="/close_cross.svg" alt="close" className="w-5 h-5" />
          </button>
          </div>
      </div>
      <div className="flex-1 overflow-y-auto px-4 max-md:grow space-y-4 overflow-x-hidden no-scrollbar pt-4 ">
        {children}
      </div>

      <div className="flex items-center gap-2 px-4 py-3">
        {/*"relative bottom-[16px] left-[16px] right-4 flex items-center space-x-2">*/}
        <div className="flex items-center grow gap-2 bg-white p-2 rounded-lg border-1 border-indira_border">
          <input
            type="text"
            className="grow bg-white px-2.5 py-1  border-indira_border rounded-[6px]  font-normal font-indira_font text-indira_text inline-block text-sm placeholder:indira_input_label_text  focus:outline-none focus:ring-0 focus:border-indira_dark_red"/>
          <div className="h-[20.5px] w-0.5 bg-indira_divider opacity-100"></div>
        </div>
        <button
          className="flex cursor-pointer  items-center justify-center w-[40px] h-[40px] bg-gradient-to-br from-indira_light_red to-indira_dark_red hover:from-indira_hover_red hover:to-indira_hover_red rounded-[8px] top-[2px] left-[318px]"
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
