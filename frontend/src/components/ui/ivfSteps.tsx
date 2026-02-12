import React from "react";


interface IVFStepsBoxProps {
    msg: {
        title: string;
        steps: string[];
    };
}


const IVFStepsBox: React.FC<IVFStepsBoxProps> = ({ msg }) => {
    return (
        <div className="bg-white font-indira_font text-indira_text px-2 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[80%] flex flex-col">
            <div className="flex flex-row items-center  w-[80%] gap-1">
                <span className="text-indira_input_label_text font-indira_font text-sm">CYCLE</span>
                <div className="h-[12px] w-0.5 bg-indira_hover_text "></div>
                <span className="text-indira_text text-[10px] font-indira_font flex items-baseline text-nowrap">{msg.title}</span>
            </div>
            <div
                className="w-full h-px my-3"
                style={{
                    border: "0",
                    borderTop: "1px solid",
                    borderImageSource:
                        "linear-gradient(90deg, rgba(229,230,230,0) 0%, #E5E6E6 50.96%, rgba(229,230,230,0) 100%)",
                    borderImageSlice: 1,
                }}
            ></div>
            <div className="mt-2 w-full flex flex-col">
                <div className="relative pl-5 pr-8">
                    <div className="absolute left-[25px] top-0 bottom-8 w-[2px] bg-indira_language_circle"></div>

                    {/* steps */}
                    {msg.steps.map((step, index) => (
                        <div key={index} className="relative flex items-start mb-6">
                            <div className=" w-3 h-3 aspect-square rounded-full bg-indira_language_circle"></div>
                            <span className="ml-4 text-xs font-medium text-nowrap">{step}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default IVFStepsBox;
