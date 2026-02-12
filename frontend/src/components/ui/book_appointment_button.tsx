import React, { useState } from "react";
import BookFreeConsultation from "@/components/container/bookFreeConsultation/bookFreeConsultation";

interface Message {
  type: "user" | "bot";
  content: string;
  contentType?: string;
}

interface BookAppointmentMessageBoxProps {
  msg: string;
  newThreadID: string;
  setTyping?: React.Dispatch<React.SetStateAction<boolean>>;
  selectedLang?: string;
  
  setThreadID?: React.Dispatch<React.SetStateAction<string | undefined>>;
  setSelectedOption?:React.Dispatch<React.SetStateAction<string>>
  setshowoptions?: React.Dispatch<React.SetStateAction<boolean>>;
  setMessages?: React.Dispatch<React.SetStateAction<Message[]>>;
}

const BookAppointmentMessageBox: React.FC<BookAppointmentMessageBoxProps> = ({
  msg,
  newThreadID,
  setTyping,
  setThreadID,
  selectedLang,
  setSelectedOption,
  setshowoptions,
  setMessages,
}) => {
  const [showForm, setShowForm] = useState<boolean>(false);

  return (
    <div className="bg-white text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs w-[75%] whitespace-pre-line">
      {msg}
      <div className="flex items-center justify-center">
        <button
          className="px-4 py-2 w-[90%] h-[25px] cursor-pointer mt-4 flex items-center justify-center text-xs text-nowrap text-indira_text font-['Open Sans'] border border-[#CE3149] rounded-[999px] bg-white  "
          style={{ pointerEvents: "auto", zIndex: 50 }}
          onClick={() => setShowForm(true)}
        >
          <span className="block overflow-hidden truncate whitespace-nowrap w-full text-center">
            Book Free Consultation
          </span>
        </button>
      </div>
      {(showForm && selectedLang) && (
        <BookFreeConsultation
          newThreadID={newThreadID}
          setTyping={setTyping}
          selectedLang={selectedLang}
          setMessages={setMessages}
          setThreadID={setThreadID}
          setSelectedOption={setSelectedOption}
          setshowoptions={setshowoptions}

        />
      )}
    </div>
  );
};

export default BookAppointmentMessageBox;
