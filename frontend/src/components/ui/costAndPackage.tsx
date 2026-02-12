import React from "react";

interface Package {
    cycle: string;
    cost: string;
    text: string;
}

interface CostAndPackageBoxProps {
    msg: {
        title: string;
        packages: Package[];
        body: string;
    };
}


const CostAndPackageBox: React.FC<CostAndPackageBoxProps> = ({ msg }) => {
    return (
        <div className="bg-white font-indira_font text-indira_text px-2 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[80%] flex flex-col">
            <div className="w-full">
                <span className="text-xs text-indira_text font-indira_font font-normal">{msg?.title}</span>
            </div>
            <div className="flex flex-col mt-2 w-full gap-2">
                {msg?.packages?.map((item: Package, index: number) => (
                    <div
                        key={index}
                        className="flex flex-col justify-between bg-indira_hello_border rounded-lg shadow "
                    >
                        <div className="flex flex-row w-full h-[50%]">
                            <span className="w-[50%] text-sm text-indira_text font-indira_font font-semibold text-nowrap pl-2 pt-2 block overflow-hidden truncate whitespace-nowrap  text-center">
                                {item?.cycle}
                            </span>
                            {/* <div className="w-[50%] h-5 bg-indira_dark_red rounded-tr-[8px] rounded-bl-[14px] flex items-center justify-center">
                                <span className="text-[10px] text-white font-indira_font block overflow-hidden truncate whitespace-nowrap w-full text-center">
                                    {item?.cost}
                                </span>
                            </div> */}
                        </div>

                        <div className="flex flex-col h-[50%] pb-2 pt-1">
                            <span className="text-[12px] text-indira_hover_text font-indira_font px-2">
                                {item?.text}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="w-full mt-4">
                <span className="text-[12px] text-indira_text font-indira_font">{msg?.body}</span>
            </div>
        </div>
    );
};

export default CostAndPackageBox;
