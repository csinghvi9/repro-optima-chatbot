import React, { useState } from "react";
import ConfirmationForm from "@/components/container/confirmationForm/confirmationForm";

interface IVFQuestionBoxProps {
  msg: string;
}

const IVFQuestionBox: React.FC<IVFQuestionBoxProps> = ({
  msg,
}) => {
  const [showForm, setShowForm] = useState<boolean>(false);

  return (
    <div className="bg-white text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs w-[75%] whitespace-pre-line">
        <div className="flex flex-col items-center justify-center">
            <img src="/ivf_photo.png"/>
        <span className="text-sm text-indira_text font-indira_font font-semibold mb-1">In Vitro Fertilization</span>
        </div>
      <span className="mt-2">{msg}</span>
    </div>
  );
};

export default IVFQuestionBox;
