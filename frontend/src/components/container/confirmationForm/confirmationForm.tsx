// import { useState, useEffect } from "react";
// import { useWebSocket } from '@/app/WebSocketContext';

// type ConfirmationFormProps = {
//   newThreadID: string;
//   setTyping: React.Dispatch<React.SetStateAction<boolean>>;
//   setShowForm: React.Dispatch<React.SetStateAction<boolean>>;
// };

// export default function ConfirmationForm({ newThreadID, setTyping,setShowForm }: ConfirmationFormProps) {
//   const [isChecked, setIsChecked] = useState<boolean>(false);
//   const [isVisible, setIsVisible] = useState<boolean>(true);
//   const { sendMessage, isConnected } = useWebSocket() as {
//     sendMessage: (message: any) => void;
//     isConnected: boolean;
//   };

//   useEffect(() => {
//     if (window.innerWidth < 768) {
//       document.body.style.overflow = "hidden";
//     }
//     return () => {
//       document.body.style.overflow = "auto";
//     };
//   }, []);
//   const handleSend = () => {

//     if (isConnected) {
//       sendMessage({ type: "message", thread_id: newThreadID, subtype: "end_flow", isflow: "end_flow" });
//       setShowForm(false);
//       setTyping(true);
//     } else {
//       console.error("WebSocket not connected");
//     }
//   };

//   if (!isVisible) return null;

//   return (

//     <div
//       className="
//       fixed inset-0 z-50
//       bg-black/30 backdrop-blur-sm
//     "
//     >
//       <div
//         className={`
//         fixed z-50 bg-white shadow-lg border border-gray-300
//         w-full h-full top-0 left-0 flex flex-col md:flex md:flex-col md:items-center md:justify-center
//         md:top-1/2 md:left-1/2 md:transform md:-translate-x-1/2 md:-translate-y-1/2
//         md:w-[850px] md:h-[473px] md:rounded-[24px]
//       `}
//       >
//         <img
//           src="/close_cross.svg"
//           alt="close"
//           className="absolute right-[2%] top-[5%] w-[20px] h-[20px] cursor-pointer"
//           onClick={() => setIsVisible(false)}
//         />

//         {/* 🔷 Top Section */}
//         <div className="absolute flex flex-col items-center justify-center h-[20%] top-[10%]">
//           <img src="/warning_icon.svg" alt="warning" className="w-[48px] h-[48px]" />
//           <p className="top-[39px] font-['Quicksand'] text-[28px] font-bold text-[#0D0D0D]">
//             Disclaimer
//           </p>
//         </div>

//         {/* Input and text section */}
//         <div className="absolute top-[177px] left-[32px] flex flex-col items-center space-x-2 w-[786px]">
//           <p className="font-['Open Sans'] text-[16px] font-light text-[#0D0D0D] align-middle">
//             The IVF Success Calculator does not provide medical advice, diagnosis or treatment.
//             The report is based on the historical data of Indira IVF and may not reflect your
//             actual chances of success during ART treatment. The report can be referred only for
//             informational purposes. The reported values are less reliable at certain ranges and
//             values of age, weight, height and previous pregnancy and ART experiences. Only doctor
//             or healthcare provider can provide a proper diagnosis and personalized treatment plan.
//           </p>

//           <label className="flex items-center mt-4 ml-8 gap-2 cursor-pointer">
//             <div className="relative flex items-center justify-center w-5 h-5">
//               <input
//                 type="checkbox"
//                 id="customCheckbox"
//                 checked={isChecked}
//                 onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
//                   setIsChecked(e.target.checked)
//                 }
//                 className="peer appearance-none w-5 h-5 border border-gray-400 rounded-sm checked:bg-[#4DBB3E] checked:border-transparent"
//               />
//               <svg
//                 className="absolute w-3 h-3 text-white hidden peer-checked:block pointer-events-none"
//                 xmlns="http://www.w3.org/2000/svg"
//                 fill="none"
//                 viewBox="0 0 24 24"
//                 stroke="currentColor"
//                 strokeWidth={3}
//               >
//                 <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
//               </svg>
//             </div>

//             <span className="text-sm text-gray-700 leading-snug">
//               I hereby declare that I have read and agreed to the terms and conditions and the
//               privacy policy.
//             </span>
//           </label>
//         </div>

//         {/* Buttons */}
//         <div className="absolute top-[387px] left-[199px] w-[424px] h-[54px] flex items-center space-x-4">
//           <button
//             className={`px-4 py-2 w-[200px] text-[20px] font-['Open Sans'] rounded-[999px] text-white ${isChecked
//                 ? "bg-gradient-to-br from-[#F04F5F] to-[#CE3149] cursor-pointer"
//                 : "bg-[#A5273A] cursor-not-allowed"
//               }`}
//             disabled={!isChecked}
//             onClick={() =>
//             (window.location.href =
//               "https://qa6.meddilink.com/#/predictor/dashboard")
//             }
//           >
//             Accept
//           </button>

//           <button
//             className={`px-4 py-2 w-[200px] text-[20px] text-[#CE3149] font-['Open Sans'] border border-[#CE3149] rounded-[999px] bg-white`}
//             disabled={!isChecked}
//             onClick={() => handleSend()}
//           >
//             Decline
//           </button>
//         </div>
//       </div>
//     </div >
//   );
// }

import { useState, useEffect } from "react";
import { useWebSocket } from "@/app/WebSocketContext";

type ConfirmationFormProps = {
  newThreadID: string;
  setTyping?: React.Dispatch<React.SetStateAction<boolean>>;
  setShowForm: React.Dispatch<React.SetStateAction<boolean>>;
};

export default function ConfirmationForm({
  newThreadID,
  setTyping,
  setShowForm,
}: ConfirmationFormProps) {
  const [isChecked, setIsChecked] = useState<boolean>(false);
  const { sendMessage, isConnected } = useWebSocket() as {
    sendMessage: (message: any) => void;
    isConnected: boolean;
  };

  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="relative overflow-y-auto no-scrollbar bg-white shadow-lg border border-gray-300 w-[90%] md:w-[850px] md:h-[420px] rounded-2xl flex flex-col p-6 max-h-[90vh]">
        {/* Close button */}
        <button
          onClick={() => setShowForm(false)}
          className="absolute right-4 top-4 text-gray-500 hover:text-gray-700 cursor-pointer"
        >
          <img src="/close_cross.svg" alt="close" className="w-5 h-5" />
        </button>

        {/* Top Section */}
        <div className="flex flex-col items-center gap-2">
          <img src="/warning_icon.svg" alt="warning" className="w-12 h-12" />
          <h2 className="font-quicksand text-2xl font-bold text-[#0D0D0D]">
            Disclaimer
          </h2>
        </div>

        {/* Text Content */}
        <div className="mt-6 flex flex-col items-center gap-4 text-center px-4 overflow-y-auto">
          <p className=" text-[16px] font-normal font-indira_font text-[#0D0D0D]">
            The Pregnancy calculator does not provide medical advice , diagnosis
            or treatment. The report is based on the historical data of
            IVF ,Clinical studies and literature sources and may not reflect
            your actual chances of success during ART treatment. The report can
            be referred only for informational purposes. The reported values are
            less reliable at certain ranges and values of age, weight , height,
            previous pregnancy etc and ART experiences. Only doctor or
            healthcare provider can provide a proper diagnosis and personalized
            treatment plan.
          </p>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isChecked}
              onChange={(e) => setIsChecked(e.target.checked)}
              className="  md:w-5 md:h-5 border border-gray-400 md:rounded-sm checked:bg-[#4DBB3E] checked:border-transparent"
            />
            <svg
              className="absolute w-3 h-3 text-white hidden peer-checked:block pointer-events-none"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="text-[16px] text-[#717272]">
              I hereby declare that I have read and agreed to the{" "}
              <a
                href="https://meddilink.com/privacy-policy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 underline"
              >
                privacy policy
              </a>{" "}
              and{" "}
              <a
                href="https://meddilink.com/terms-and-conditions"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 underline"
              >
                T&amp;C
              </a>
            </span>
          </label>
        </div>

        {/* Buttons */}
        <div className="mt-[5%] flex justify-center gap-4">
          <button
            disabled={!isChecked}
            onClick={() =>
              window.open(
                "https://successcalculator.indiraivf.in/#/predictor/form?step=1&substep=1",
                "_blank",
                "noopener,noreferrer"
              )
            }
            className={`px-6 py-2 w-[50%] md:w-[20%] text-lg font-open-sans rounded-full text-white cursor-pointer ${
              isChecked
                ? "bg-gradient-to-br from-[#F04F5F] to-[#CE3149] hover:opacity-90"
                : "bg-[#A5273A] cursor-not-allowed"
            }`}
          >
            Accept
          </button>
          <button
            disabled={!isChecked}
            onClick={() => setShowForm(false)}
            className="px-6 py-2 w-[50%] md:w-[20%] cursor-pointer text-sm md:text-lg font-open-sans rounded-full border border-[#CE3149] text-[#CE3149] bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Decline
          </button>
        </div>
      </div>
    </div>
  );
}
