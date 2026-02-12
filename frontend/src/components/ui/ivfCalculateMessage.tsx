import React, { useState } from "react";
import ConfirmationForm from "@/components/container/confirmationForm/confirmationForm";

interface IVFCalculateMessageBoxProps {
  msg: string;
  newThreadID: string;
  setTyping?: React.Dispatch<React.SetStateAction<boolean>>;
}

const IVFCalculateMessageBox: React.FC<IVFCalculateMessageBoxProps> = ({
  msg,
  newThreadID,
  setTyping,
}) => {
  const [showForm, setShowForm] = useState<boolean>(false);
  return (
    <div className="bg-white text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs w-[75%] whitespace-pre-line">
      {msg}
      <div className="flex items-center justify-center">
        <button
          className="px-4 py-2 w-[90%] h-[25px] mt-4 flex items-center justify-center text-xs text-indira_text font-['Open Sans'] border border-[#CE3149] rounded-[999px] bg-white cursor-pointer"
          onClick={() => setShowForm((prev) => !prev)} 
        >
          Calculate Now
        </button>
      </div>
      {showForm && (
        <ConfirmationForm
          newThreadID={newThreadID}
          setTyping={setTyping}
          setShowForm={setShowForm}
        />
      )}
    </div>
  );
};

export default IVFCalculateMessageBox;
