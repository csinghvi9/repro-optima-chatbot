import React from "react";

interface SuccessRateMessageProps {
    msg: {
        first_text: string;
        second_heading: string;
        second_text: string;
    };
}

const SuccessRateMessage: React.FC<SuccessRateMessageProps> = ({ msg }) => {
    return (
        // <div className="w-full relative space-y-2 flex flex-row  p-4 rounded-[10px] gap-2 ml-8 ">
        //     {/* Left section */}
        //     <div className="w-[50%] flex flex-col  bg-[#fff9fb]  ">

        //         <img
        //             src="./indira_logo.svg"
        //             alt="logo"
        //             className="w-[50%] h-[90%] pl-4 pt-4"
        //         />
        //         <p className="text-indira_font font-indira_font text-xs p-4">{msg.first_text}</p>

        //         <div className="flex items-end">
        //         <img src="./doctors.svg" className="w-[100%] h-[90%] " />
        //         </div>

        //     </div>

        //     {/* Right section */}
        //     <div className="w-[50%] flex flex-col items-center bg-[#fff9fb]  pl-4 rounded-[10px]">
        //         {/* Left side text */}
        //         <div className="flex flex-col flex-1 h-[40%]">
        //             <h2 className="text-[16px] text-indira_dark_red font-semibold font-indira_font">
        //                 {msg.second_heading}
        //             </h2>
        //             <p className="text-indira_text text-base font-normal font-indira_font mt-1">
        //                 {msg.second_text}
        //             </p>
        //         </div>

        //         {/* Right side image */}
        //         <div className="flex items-end justify-end h-[50%]">
        //             <img
        //                 src="./parents.svg"
        //                 className="w-[120px] h-full object-contain"
        //                 alt="happy couple"
        //             />
        //         </div>
        //     </div>
        // </div>
        <div className="w-full flex flex-row gap-2 pl-10">
            {/* Left card */}
            <div className="flex flex-col w-[50%] bg-[#fff9fb] border border-indira_divider rounded-[10px] ">
                <img
                    src="./iivf_logo.png"
                    alt="logo"
                    className="w-[70%] h-[20%] pl-4 pt-4"
                />
                <p className="font-indira_font text-xs mt-2 pl-2 md:pl-4  w-[90%] text-indira_text">{msg.first_text}</p>
                <div className="mt-auto">
                    <img src="./doctors.svg" className="w-full object-contain rounded-b-[10px]" alt="doctors" />
                </div>
            </div>

            {/* Right card */}
            <div className="flex flex-col items-center w-[50%] bg-[linear-gradient(299.72deg,rgba(251,248,255,0.5)_53.78%,#FFFFFF_100%)] border border-indira_divider rounded-[10px] pl-2 md:pl-4  pt-2">
                <div className="flex flex-col flex-1 h-[30%] md:h-[40%]">
                    <h2 className="text-[16px] text-indira_dark_red font-semibold font-indira_font text-nowrap">
                        {msg.second_heading}
                    </h2>
                    <p className="text-indira_text text-[12px] font-normal font-indira_font mt-1">
                        {msg.second_text}
                    </p>
                </div>
                <div className="flex w-full h-[70%] md:h-[60%] items-end justify-end">
                    <img
                        src="./parents.svg"
                        className=" h-auto object-contain rounded-b-[10px]"
                        alt="happy couple"
                    />
                </div>
            </div>
        </div>

    );
};

export default SuccessRateMessage;