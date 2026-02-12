import React, { useMemo, useState } from "react";
import { useWebSocket } from "@/app/WebSocketContext";

type TimeSlot = { value: string; disabled?: boolean };

interface TimeSlotsMessageProps {
  newThreadID: string;
  setTyping: React.Dispatch<React.SetStateAction<boolean>>;
  onSelectTimeSlot: (time: string) => void;
  previousMessages: { type: string; content: string }[];
  slots?: TimeSlot[];
  initialVisible?: number; // default: 8
  botAvatar?: React.ReactNode;
  // optional custom icon
}

const defaultSlots: TimeSlot[] = [
  { value: "09:00 AM" }, { value: "09:30 AM" }, { value: "10:00 AM" }, { value: "10:30 AM" },
  { value: "11:00 AM" }, { value: "11:30 AM" }, { value: "12:00 PM" }, { value: "12:30 PM" },
  { value: "01:00 PM" }, { value: "01:30 PM" }, { value: "02:00 PM" }, { value: "02:30 PM" },
  { value: "03:00 PM" }, { value: "03:30 PM" }, { value: "04:00 PM" }, { value: "04:30 PM" },
  { value: "05:00 PM" }, { value: "05:30 PM" }, { value: "06:00 PM" }, { value: "06:30 PM" },
];

const TimeSlotsMessage: React.FC<TimeSlotsMessageProps> = ({
  newThreadID,
  setTyping,
  onSelectTimeSlot,
  previousMessages,
  slots,
  initialVisible = 8,

}) => {
  const { sendMessage, isConnected } = useWebSocket() as {
    sendMessage: (message: any) => void;
    isConnected: boolean;
  };

  const [expanded, setExpanded] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [locked, setLocked] = useState(false); // disables the whole grid after a pick
  const allSlots = useMemo(() => slots ?? defaultSlots, [slots]);
  const visible = expanded ? allSlots : allSlots.slice(0, initialVisible);

  const send = (time: string) => {
    if (!isConnected) return;
    // time is already a string like "10:30 AM"
    sendMessage({
      type: "message",
      thread_id: newThreadID,
      message: time,
      subtype: "appointment",
      isflow: "not confirm",
    });
    setTyping(true);
  };

  const pick = (time: string, disabled?: boolean) => {
    if (disabled || locked) return;
    setSelected(time);
    onSelectTimeSlot(time);
    send(time);
    setLocked(true); // lock the grid after one selection
  };
  const now = new Date(); // current time
  const todayDate = now.toISOString().split("T")[0]; // YYYY-MM-DD

  // Assume you get the selected date from the previous message:
  const selectedDateString = previousMessages[previousMessages.length - 2]?.content; // e.g., '2025-09-23'

  const slotsToShow = useMemo(() => {
    const slotsArray = slots ?? defaultSlots;
    if (!selectedDateString) return slotsArray;

    // add 30-minute buffer
    const bufferNow = new Date(now.getTime() + 30 * 60000);

    return slotsArray.map(slot => {
      let isDisabled = slot.disabled ?? false;

      if (selectedDateString === todayDate) {
        // parse time string like "04:00 PM"
        const [time, meridiem] = slot.value.split(" ");
        let [hours, minutes] = time.split(":").map(Number);
        if (meridiem === "PM" && hours !== 12) hours += 12;
        if (meridiem === "AM" && hours === 12) hours = 0;

        const slotDate = new Date();
        slotDate.setHours(hours, minutes, 0, 0);

        // disable if slot is before bufferNow
        if (slotDate <= bufferNow) {
          isDisabled = true;
        }
      }

      return { ...slot, disabled: isDisabled };
    });
  }, [slots, selectedDateString, now]);

  return (
    <div className="w-full relative space-y-2">

      {/* FULL-WIDTH SHEET behind bubble (z-10). Negative margin tucks it under the bubble edge */}
      <section
        className={[
          "relative flex flex-col items-center z-10 -mt-1 ",
          locked ? "opacity-70 pointer-events-none" : "",
        ].join(" ")}
      >
        {/* Grid */}
        <div
          className={`overflow-hidden duration-300 ease-in-out w-full 
            ${expanded ? "h-auto" : "h-[120px]"} `
          }
        >
          <div className="p-3 grid grid-cols-4 gap-2 sm:gap-3">
            {slotsToShow.map(({ value, disabled }) => {

              const isSel = selected === value;
              return (
                <button
                  key={value}
                  type="button"
                  onClick={() => pick(value, disabled)}
                  disabled={!!disabled || locked}
                  aria-pressed={isSel}
                  className={[
                    "rounded-xl border text-xs font-semibold transition h-[34px] w-full cursor-pointer",
                    "shadow-[0_1px_0_rgba(0,0,0,0.04)] focus:outline-none focus:ring-2 focus:ring-offset-1",
                    disabled || locked
                      ? "opacity-40 cursor-not-allowed bg-gray-100 text-gray-400"
                      : "bg-white text-indira_hover_text border-gray-200 hover:bg-gray-50",
                  ].join(" ")}
                  title={disabled ? "Not available" : "Select this time"}
                >
                  {value}
                </button>
              );
            })}
          </div>
        </div>

        {/* Transparent → blur fade when collapsed */}
        {!expanded && !locked && (
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-gradient-indira pointer-events-none" />
        )}
        {/* View More / Less row */}
        <button
          type="button"
          onClick={() => setExpanded(prev => !prev)}
          className="relative cursor-pointer z-20 text-xs font-medium text-indira_text  inline-flex items-center gap-1 text-center mt-4"
          disabled={locked}
        >
          {expanded ? 'View Less' : 'View More'}
          <img
            src="./dropdown_arrow.svg" // <-- replace with your icon path
            alt="toggle"
            className={`w-4 h-4 transition-transform duration-300 ${expanded ? "rotate-180" : ""
              }`}
          />
        </button>
      </section>
    </div>
  );
};

export default TimeSlotsMessage;
