import React from "react";

interface EmergencyMessageBoxProps {
  msg: string;
}

const EmergencyMessageBox: React.FC<EmergencyMessageBoxProps> = ({ msg }) => {
  return (
    <div className="bg-white font-indira_font text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%] flex flex-col">
      {msg}
    </div>
  );
};

export default EmergencyMessageBox;
