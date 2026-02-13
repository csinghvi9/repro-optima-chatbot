import React, { useEffect } from "react";

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm p-4">
      <div className="relative bg-white shadow-2xl w-full max-w-sm rounded-3xl overflow-hidden flex flex-col items-center">
        {/* Close button */}
        <button
          onClick={() => setSubmittedForm(false)}
          className="absolute right-4 top-4 z-20 text-gray-400 hover:text-gray-600 cursor-pointer transition-colors"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {/* Top gradient section */}
        <div className="w-full bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 pt-10 pb-8 px-6 flex flex-col items-center">
          {/* Animated checkmark */}
          <div className="w-20 h-20 rounded-full bg-white shadow-lg flex items-center justify-center mb-5">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
          </div>

          <h2 className="text-xl font-bold text-gray-800 tracking-tight">
            Thank You!
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Your request has been submitted
          </p>
        </div>

        {/* Content section */}
        <div className="px-6 py-6 flex flex-col items-center w-full">
          {/* Reference number card */}
          <div className="w-full bg-gray-50 rounded-xl px-4 py-3 flex items-center justify-between mb-4">
            <span className="text-xs text-gray-500 font-medium">Reference No.</span>
            <span className="text-sm font-bold text-gray-800 tracking-wide">{response}</span>
          </div>

          <p className="text-sm text-gray-500 text-center leading-relaxed mb-6">
            Our team will review your details and get in touch with you shortly.
          </p>

          {/* Button */}
          <button
            className="w-full py-3 text-sm font-semibold text-white rounded-full bg-gradient-to-r from-[#F04F5F] to-[#CE3149] hover:opacity-90 transition-opacity cursor-pointer"
            onClick={() => setSubmittedForm(false)}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
