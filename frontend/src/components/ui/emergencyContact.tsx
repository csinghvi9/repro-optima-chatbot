import React, { useState } from "react";
import LoanEMIForm from "@/components/ui/LoanEMIForm";
import RequestSubmitted from "@/components/ui/requestSubmitted";

interface EmergencyMessageBoxProps {
  msg: string;
}

const EmergencyMessageBox: React.FC<EmergencyMessageBoxProps> = ({ msg }) => {
  return (
    <div className="bg-white font-indira_font text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%] flex flex-col">
      <a
        href="https://api.whatsapp.com/send/?phone=917230096667&text=Hello&type=phone_number&app_absent=0"
        target="_blank"
        rel="noopener noreferrer"
        className="bg-[#4DBB3E] aspect-square rounded-full w-[20%] h-[20%] flex items-center justify-center mb-2 hover:opacity-90 transition"
      >
        <img src="./whats_app.svg" className="w-[50%] h-[50%]" alt="WhatsApp" />
      </a>
      {msg}
    </div>
  );
};

export default EmergencyMessageBox;
