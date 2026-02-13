// import React from "react";

// interface AppointmentBookedMessageProps {
//     msg: {
//         content: {
//             Date: string;
//             Time: string;
//             City: string;
//             State: string;
//         };
//     };
// }

// const AppointmentBookedMessage: React.FC<AppointmentBookedMessageProps> = ({ msg }) => {
//     return (
//         <div className="bg-white text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs w-full whitespace-pre-line">
//             {/* Success Banner */}
//             <div className="flex item-center justify-center">
//                 <div className="bg-[#EDF9EC] p-3 rounded-[10px]  w-full flex flex-col items-center justify-center">
//                     <div className="rounded-full bg-[#72CC66] w-[18px] h-[18px] flex items-center justify-center ">
//                         <img src="/right.svg" alt="success" className="w-3 h-3" />
//                     </div>
//                     <div className="mt-2 w-full flex items-center bg-[#DCF2D9] justify-center px-3 py-1 rounded-[999px] text-nowrap">
//                         <p className="text-xs font-indira_font text-[#717272] text-nowrap">
//                             Appointment booked
//                         </p>
//                     </div>
//                 </div>
//             </div>

//             {/* Date & Time */}
//             <div className="flex justify-between mt-2 mb-4 p-1">
//                 <div>
//                     <p className="text-[10px] text-gray-500 font-semibold">DATE</p>
//                     <p className="text-sm font-semibold">{msg.content.Date}</p>
//                 </div>
//                 <div className="text-right">
//                     <p className="text-[10px] text-gray-500 font-semibold">TIME</p>
//                     <p className="text-sm font-semibold">{msg.content.Time}</p>
//                 </div>
//             </div>

//             {/* Location & Map */}
//             <div className="flex items-center justify-between">
//                 <div>
//                     <div className="flex items-center gap-2">
//                         <img src="/location.svg" alt="location" className="w-5 h-5" />
//                         <div className="flex flex-col">
//                             <p className="font-semibold font-indira_font text-xs">
//                                 {msg.content.City}
//                             </p>
//                             <p className="font-normal font-indira_font text-xs text-[#717272]">
//                                 {msg.content.State}
//                             </p>
//                         </div>
//                     </div>
//                 </div>

//                 <div className="flex justify-center items-center ">
//                     <div className="w-[32px] h-[32px] rounded-full flex items-center justify-center bg-indira_user_message_bg cursor-pointer">
//                         <img
//                             src="/map_direction.svg"
//                             alt="map direction"
//                             className="w-5 h-5"
//                         />
//                     </div>
//                 </div>
//             </div>
//         </div>
//     );
// };

// export default AppointmentBookedMessage;
import React from "react";

interface AppointmentBookedMessageProps {
  msg: {
    content: {
      first_text: string;
      second_text: string;
      third_text: string;
    };
  };
}

const AppointmentBookedMessage: React.FC<AppointmentBookedMessageProps> = ({
  msg,
}) => {
  return (
    <div className="bg-white ml-1 text-indira_text  rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs w-full whitespace-pre-line">
      <div className="relative  text-center overflow-hidden rounded-xl shadow-md bg-[#DCF2D9] [clip-path:ellipse(110%_80%_at_50%_10%)] pl-10 pr-10 pb-10 pt-5">
        <div className="relative z-10 flex flex-col items-center">
          <div className=" w-[30%]  aspect-square rounded-full bg-white border border-[#4DBB3E] grid place-items-center">
            <div className="w-[60%] aspect-square rounded-full bg-[#72CC66] grid place-items-center">
              <img src="/right.svg" className="w-[60%] h-[60%]" />
            </div>
          </div>
          <h2 className="text-sm mt-2 font-semibold text-indira_text ">
            {msg.content.first_text}
          </h2>
        </div>
      </div>
      <div className=" flex flex-col justify-center items-center pl-3 pr-1 pb-2">
        <p className="flex items-center justify-center mt-3  text-indira_hover_text text-xs font-semibold w-full font-indira_font">
          {msg.content.second_text}
        </p>

        <p className="flex flex-wrap items-center justify-center mt-2 text-indira_hover_text text-xs w-full font-indira_font font-light">
          {msg.content?.third_text.split(/(\d+)/).map((part, index) =>
            /^\d+$/.test(part) ? (
              <span
                key={index}
                className="underline font-semibold inline-block whitespace-nowrap"
              >
                {part}
              </span>
            ) : (
              <span key={index}>{part}</span>
            )
          )}
        </p>
      </div>
    </div>
  );
};

export default AppointmentBookedMessage;
