import React, { useEffect, useState } from "react";
import { Calendar } from "@heroui/calendar";
import { today, getLocalTimeZone } from "@internationalized/date";
import { useWebSocket } from '@/app/WebSocketContext';

interface CalendarMessageProps {
    text: string;
    newThreadID: string;
    setTyping: React.Dispatch<React.SetStateAction<boolean>>;
    onSelectDate: (date: string) => void;
    showCalendar:boolean;
    setShowCalendar:React.Dispatch<React.SetStateAction<boolean>>;

}

const CalendarMessage: React.FC<CalendarMessageProps> = ({ text, newThreadID, setTyping, onSelectDate,setShowCalendar,showCalendar }) => {
    const { sendMessage, isConnected } = useWebSocket() as {
        sendMessage: (message: any) => void;
        isConnected: boolean;
    };
    useEffect(() => {
    setShowCalendar(true);
  }, []);
    const handleSend = (formatted: string) => {
        if (formatted.trim()) {

            if (isConnected) {
                sendMessage({ type: "message", thread_id: newThreadID, message: formatted, subtype: "appointment", isflow: "not confirm" });
                setTyping(true);
            } else {
                console.error("WebSocket not connected");
            }
        }
    };
    return (
        <div className="flex flex-col items-start pl-2 ">
            {/* Bot message bubble */}
            <div className="flex w-full bg-white rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] overflow-hidden">
                <div className="flex-[3] p-2 text-xs text-indira_text">{text}</div>

                <div
                    className="flex-[1] flex items-center justify-center cursor-pointer"
                    onClick={() => setShowCalendar((prev) => !prev)}
                >
                    <div className="w-[32px] h-[32px] rounded-[8px] flex items-center justify-center bg-indira_user_message_bg">
                        <img src="/calendar_icon.svg" alt="calendar" className="w-5 h-5" />
                    </div>
                </div>
            </div>

            {/* Calendar bubble */}
            {showCalendar && (
                <div className="w-full flex justify-start">
                    <div className="bg-white mt-2 rounded-lg border border-gray-200 shadow-sm w-full max-w-full ">
                        <Calendar
                            aria-label="Select Date"
                            defaultValue={today(getLocalTimeZone())}
                            minValue={today(getLocalTimeZone())}
                            onChange={(date: any) => {
                                if (date) {
                                    const formatted = date.toString();
                                    onSelectDate(formatted);
                                    handleSend(formatted);
                                    setShowCalendar(false);
                                }
                            }}
                            classNames={{
                                base: "w-full h-auto overflow-hidden",
                                content: "w-full h-auto", // full width for responsiveness
                                headerWrapper: "py-1 flex justify-between items-center",
                                title: "text-xs font-medium truncate mt-[10px] text-black",
                                nextButton: "w-6 h-6 text-gray-600 hover:text-black mt-[10px]",
                                prevButton: "w-6 h-6 text-gray-600 hover:text-black mt-[10px]",
                                grid: "w-[90%] ml-[12px] mt-[10px]",
                                gridHeader: "text-xs p-0 text-black",
                                gridHeaderRow: 'p-0',
                                cell: "p-0 text-xs",
                                cellButton:
                                    "w-8 h-8 rounded-full flex items-center justify-center " +
                                    "text-black dark:text-black " +                       // default text
                                    "data-[disabled=true]:text-gray-400 " + // past dates
                                    "hover:bg-black hover:text-white data-[disabled=true]:hover:bg-white ",// future dates hover
                            }}
                            weekdayStyle="narrow"
                        />
                    </div>
                </div>
            )}
        </div>
    );

};

export default CalendarMessage;
