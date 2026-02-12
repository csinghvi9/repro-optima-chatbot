import React, {useState} from "react";
import LoanEMIForm from "@/components/ui/LoanEMIForm"
import RequestSubmitted from "@/components/ui/requestSubmitted"

interface LoanAndEMIBoxProps {
    msg: string
    newThreadID: string;
}

const LoanAndEMIBox: React.FC<LoanAndEMIBoxProps> = ({ msg,newThreadID }) => {
    const [showForm, setShowForm] = useState<boolean>(false);
    const [submittedForm, setSubmittedForm] = useState<boolean>(false);
    const [response, setResponse] = useState<number>(0);
    return (
        <div
            className="relative overflow-hidden rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs flex flex-col max-w-[60%] pt-2 pl-2 border border-[#E5E6E6]"
            style={{ background: "var(--Lightorange-50, #FFF8EB)" }}
        >
            {/* HEX BG */}

            {/* CONTENT (put above with z-10) */}

            <span className="text-indira_text font-indira_font text-[16px] font-medium">Get</span>
            <span className="text-indira_text font-indira_font text-[20px] font-semibold">LOAN</span>
            <span className="text-[#717272] font-indira_font text-[12px] font-medium mt-[4px] pr-2">
                {msg}
            </span>

            <div className="flex flex-row mt-4">
                <div className="w-[50%] flex justify-center items-center">
                    <button className="relative w-full h-[30px] rounded-full p-[1px] bg-gradient-to-r from-[#CE3149] to-[#FFF5F7] hover:opacity-90 cursor-pointer"
                    onClick={() => setShowForm((prev) => !prev)}
                    >
                        <span className="flex items-center justify-center w-full h-full rounded-full bg-white font-semibold text-indira_text px-6 py-2 md:text-xs text-[10px] text-nowrap">
                            Apply Now
                        </span>
                    </button>
                </div>
                <div className="w-[50%]  flex justify-end">

                    <img src="./money.svg" className="h-[90px]  " />
                </div>
            </div>
        {showForm && (
                    <LoanEMIForm
                      newThreadID={newThreadID}
                      setShowForm={setShowForm}
                      showForm={showForm}
                      setSubmittedForm={setSubmittedForm}
                      setResponse={setResponse}
                    />
        )}
        {submittedForm && (
                        <RequestSubmitted setSubmittedForm={setSubmittedForm} response={response}/>
                    )}
        </div>
    );
};

export default LoanAndEMIBox;
