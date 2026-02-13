import React from "react";

const Typing: React.FC = () => {
  return (
    <div className="flex items-center space-x-1 mt-5 ml-3">
      <div className="dot bg-indira_border w-[5px] h-[5px] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      <div className="dot bg-indira_border w-[5px] h-[5px] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
      <div className="dot bg-indira_border w-[5px] h-[5px] rounded-full animate-bounce"></div>
    </div>
  );
};

export default Typing;
