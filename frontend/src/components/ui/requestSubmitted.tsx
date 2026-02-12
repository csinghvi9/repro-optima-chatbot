import { useState, useEffect } from "react";

type RequestSubmittedProps = {
  setSubmittedForm: React.Dispatch<React.SetStateAction<boolean>>;
  response: number;
};

export default function RequestSubmitted({
  setSubmittedForm,
  response,
}: RequestSubmittedProps) {
  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  return (
    // <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
    //     <div className="relative bg-white shadow-lg border border-gray-300
    //           w-[90%] md:w-[50%] lg:w-[30%] h-[80%] md:h-[75%] lg:h-[75%] rounded-2xl overflow-hidden
    //           flex flex-col items-center ">

    //         {/* SVG Background (absolute, centered, responsive) */}
    //         {/* <div className="absolute
    //             w-full h-[30%] pointer-events-none">
    //             <img
    //                 src="./ellipse.svg"
    //                 alt="background ellipse"
    //                 className="w-full h-auto"
    //             />
    //         </div> */}

    //         {/* Foreground content */}
    //         <div className="relative flex flex-col items-center text-center h-[50%] w-full py-10 ">
    //             {/* Ellipse background */}
    //             <button
    //                 onClick={() => setSubmittedForm(false)}
    //                 className="absolute right-5 top-4 text-gray-500 hover:text-gray-700 cursor-pointer"
    //             >
    //                 <img src="/close_cross.svg" alt="close" className="w-5 h-5" />
    //             </button>
    //             <img
    //                 src="/ellipse.svg"
    //                 alt="ellipse background"
    //                 className="absolute top-0 left-1/2 -translate-x-1/2 w-[140%] md:w-[120%] lg:w-[100%] h-full pointer-events-none"
    //             />

    //             {/* Foreground content */}
    //             <div className="relative  flex flex-col items-center text-center md:px-6">

    //                 <div className=" w-[30%] md:w-[25%] lg:w-[30%] aspect-square rounded-full bg-white border border-[#4DBB3E] grid place-items-center">
    //                     <div className="w-[60%] aspect-square rounded-full bg-[#72CC66] grid place-items-center">
    //                         <img src="/right.svg" className="w-[60%] h-[60%]" />
    //                     </div>
    //                 </div>

    //                 <h2 className=" mt-2 sm:mt-4  text-[20px] sm:text-[28px] w-[70%] md:w-[80%] lg:w-[70%] font-indira_second_font font-bold text-indira_text">
    //                     REQUEST SUBMITTED
    //                 </h2>
    //             </div>

    //         </div>
    //         <div className="relative flex flex-col items-center text-center h-[50%] w-full ">
    //             <p className="mt-3 text-indira_hover_text text-sm md:text-base w-[70%] font-indira_font">
    //                 Your request is registered with <br />
    //                 <span className="font-semibold text-indira_text text-xs md:text-sm">Reference number : {response}</span>
    //             </p>

    //             <p className="mt-2 text-indira_hover_text text:sm md:text-base w-[80%] font-indira_font">
    //                 Thanks for sharing your details, someone from our team will contact you shortly
    //             </p>

    //             {/* Button */}
    //             <button className=" mt-4 md:mt-6 md:px-8 md:py-2 text-sm md:text-[16px] text-white font-semibold rounded-[999px]
    //                bg-gradient-to-r from-indira_light_red to-indira_dark_red w-[70%] h-[15%] font-indira_font cursor-pointer"
    //                onClick={() => setSubmittedForm(false)}>
    //             Got it
    //             </button>
    //         </div>
    //     </div>
    // </div>
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div
        className="relative bg-white shadow-lg border border-gray-300 
                  w-[90%]  md:w-[50%] lg:w-[30%] rounded-2xl overflow-hidden 
                  flex flex-col items-center "
      >
        <div className="relative w-full   text-center overflow-hidden rounded-xl shadow-md [background:linear-gradient(135deg,#F5FFB4_0%,#BBEFFF_100%)] [clip-path:ellipse(110%_80%_at_50%_10%)] pl-10 pr-10 pb-10 pt-5">
          <button
            onClick={() => setSubmittedForm(false)}
            className="absolute right-5 top-4 text-gray-500 hover:text-gray-700 cursor-pointer"
          >
            <img src="/close_cross.svg" alt="close" className="w-5 h-5" />
          </button>
          <div className="relative z-10 flex flex-col items-center pt-6">
            <div className=" w-[20%] md:w-[30%] md:mt-3 lg:w-[20%] lg:mt-1   aspect-square rounded-full bg-white border border-[#4DBB3E] grid place-items-center">
              <div className="w-[60%] aspect-square rounded-full bg-[#72CC66] grid place-items-center">
                <img src="/right.svg" className="w-[60%] h-[60%]" />
              </div>
            </div>
            <h2 className=" mt-2 sm:mt-4  text-[20px] sm:text-[28px] w-[70%]  font-indira_second_font font-bold text-indira_text">
              REQUEST SUBMITTED
            </h2>
          </div>
        </div>
        <div className="relative flex flex-col items-center text-center  w-full pb-5">
          <p className="mt-3 text-indira_hover_text text-sm md:text-base w-[70%] font-indira_font">
            Your request is registered with <br />
            <span className="font-semibold text-indira_text text-xs md:text-sm">
              Reference number : {response}
            </span>
          </p>

          <p className="mt-2 text-indira_hover_text text:sm md:text-base w-[80%] font-indira_font">
            Thanks for sharing your details, someone from our team will contact
            you shortly
          </p>

          {/* Button */}
          <button
            className=" mt-4 md:mt-6 md:px-8 md:py-2 text-sm md:text-[16px] text-white font-semibold rounded-[999px] 
                       bg-gradient-to-r from-indira_light_red to-indira_dark_red w-[70%]  font-indira_font cursor-pointer"
            onClick={() => setSubmittedForm(false)}
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
