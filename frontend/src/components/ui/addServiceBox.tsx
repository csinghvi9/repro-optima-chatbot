import React, { useState } from "react";
import RequestSubmitted from "@/components/ui/requestSubmitted";
import userInformation from "@/components/user_info/user_info";
import { useWebSocket } from "@/app/WebSocketContext";

interface AddOnServiceBoxProps {
  msg: string;
}

const AddOnServiceBox: React.FC<AddOnServiceBoxProps> = ({ msg }) => {
  const [submittedForm, setSubmittedForm] = useState<boolean>(false);
  const [response, setResponse] = useState<number>(0);
  const { updateUserInfo, generateReferenceNumber } = userInformation();
  const { isConnected } = useWebSocket() as {
    isConnected: boolean;
  };
  const handleSend = async () => {
    if (isConnected) {
      const response = await generateReferenceNumber();
      setResponse(response);
    } else {
      console.error("WebSocket not connected");
    }
  };
  return (
    <div
      className="font-indira_font text-indira_text border border-indira_divider rounded-tl-[10px] rounded-tr-[10px] 
                     rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[80%] flex flex-row"
      style={{
        background: `linear-gradient(0deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)),
                 linear-gradient(151.22deg, #EEFCFF 25%, rgba(255, 255, 255, 0.7) 60%, #FFFFFF 80.36%)`,
      }}
    >
      <div className="flex flex-col w-full pl-2 py-2">
        <span className="text-indira_text text-xs font-semibold">{msg}</span>
        {/* <button
          onClick={() => {
            setSubmittedForm(true);
            handleSend();
          }}
          className="px-4 py-2 w-[60%] mt-4 font-semibold rounded-[999px] relative overflow-hidden text-indira_text cursor-pointer"
          style={{
            background:
              "linear-gradient(99.11deg, #53D1EC 7.14%, rgba(83, 209, 236, 0) 108.09%)",
            padding: "2px", // this acts as the border thickness
          }}
        >
          <span
            className="block w-full h-full rounded-[999px] bg-white text-center block overflow-hidden truncate whitespace-nowrap"
            style={{ lineHeight: "24px" }} // adjust to button height
          >
            View plans
          </span>
        </button> */}
      </div>
      <div className=" flex items-center justify-center">
        <img
          src="./hormone_structure.svg"
          className="max-w-full h-full"
          alt="Hormone Structure"
        />
      </div>
      {submittedForm && (
        <RequestSubmitted
          setSubmittedForm={setSubmittedForm}
          response={response}
        />
      )}
    </div>
  );
};

export default AddOnServiceBox;
