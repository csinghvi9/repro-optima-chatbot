import React from "react";
import { useWebSocket } from "@/app/WebSocketContext";

interface Center {
  "Clinic Name": string;
  Distance_km: number | string;
  [key: string]: any; // in case extra fields come
}
interface Message {
  type: "bot" | "user";
  content: string | Record<string, any>;
  contentType?: string;
}

interface CentersListProps {
  centers: Center[];
  onSelect?: (city: string) => void;
  newThreadID: string;
  setTyping?: React.Dispatch<React.SetStateAction<boolean>>;
  messages?: Message[];
}

const CentersList: React.FC<CentersListProps> = ({
  centers,
  onSelect,
  newThreadID,
  setTyping,
  messages,
}) => {

  if (!centers || centers.length === 0) {
    return (
      <div className="bg-white text-indira_text px-3 py-2 rounded-lg text-xs max-w-[75%]">
        No centers found.
      </div>
    );
  }
  const { sendMessage, isConnected } = useWebSocket() as {
    sendMessage: (message: any) => void;
    isConnected: boolean;
  };
  const handleSend = (formatted: string) => {
    if (formatted.trim()) {
      if (isConnected) {
        sendMessage({
          type: "message",
          thread_id: newThreadID,
          message: formatted,
          subtype: "appointment",
          isflow: "not confirm",
        });
        if (setTyping) {
          setTyping(true);
        }
      } else {
        console.error("WebSocket not connected");
      }
    }
  };

  const handleOpenMapDirection = (center: Center) => {
    if (center.url) {
      window.open(center.url, "_blank");
    } else {
      const destination = encodeURIComponent(center["Clinic Name"]);
      window.open(`https://www.google.com/maps/search/?api=1&query=${destination}`, "_blank");
    }
  };

  return (
    <div className="bg-white px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[80%]">
      <p className="text-indira_text mb-2 text-xs">
        Here is our clinic location:
      </p>

      <ul className="space-y-2">
        {/* If NO messages → Non-clickable list */}
        {!messages || messages.length === 0
          ? centers.map((center, idx) => (
              <li
                key={idx}
                className="h-[48px] flex flex-col justify-center rounded hover:bg-gray-100"
                style={{
                  borderBottom: "1px solid",
                  borderImageSlice: 1,
                  borderImageSource:
                    "linear-gradient(90deg, rgba(229, 230, 230, 0) 0%, #E5E6E6 50.96%, rgba(229, 230, 230, 0) 100%)",
                }}
              >
                <div className="flex flex-row">
                  <div className="flex justify-between items-center w-[75%]">
                    <div className="w-[70%]">
                      <span className="text-indira_dark_red font-semibold cursor-default">
                        {center["Clinic Name"].split(" - ").pop()}
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center w-[25%]">
                    <div className="flex justify-center items-center w-full">
                      <button
                        type="button"
                        className="w-[32px] h-[32px] rounded-full flex items-center justify-center bg-indira_user_message_bg cursor-pointer hover:opacity-90 transition"
                      >
                        <img
                          src="/map_direction.svg"
                          alt="map"
                          className="w-5 h-5"
                        />
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))
          : /* If messages exist → Clickable list */
            centers.map((center, idx) => {
              return (
                <li
                  key={idx}
                  className="h-[48px] flex flex-col justify-center rounded hover:bg-gray-100"
                  style={{
                    borderBottom: "1px solid",
                    borderImageSlice: 1,
                    borderImageSource:
                      "linear-gradient(90deg, rgba(229, 230, 230, 0) 0%, #E5E6E6 50.96%, rgba(229, 230, 230, 0) 100%)",
                  }}
                >
                  <div className="flex flex-row">
                    <div className="flex justify-between items-center w-[75%]">
                      <div className="w-[70%]">
                        <span
                          className="text-indira_dark_red font-semibold cursor-pointer hover:underline"
                          onClick={() => {
                            onSelect?.(
                              center["Clinic Name"].split(" - ").pop()!
                            );
                            handleSend(center["Clinic Name"]);
                          }}
                        >
                          {center["Clinic Name"].split(" - ").pop()}
                        </span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center w-[25%]">
                      <div className="flex justify-center items-center w-full">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenMapDirection(center);
                          }}
                          className="w-[32px] h-[32px] rounded-full flex items-center justify-center bg-indira_user_message_bg cursor-pointer hover:opacity-90 transition"
                        >
                          <img
                            src="/map_direction.svg"
                            alt="map"
                            className="w-5 h-5"
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
      </ul>

      <p className="text-xs text-indira_text mt-2">
        Use the map icon to view the location on Google Maps.
      </p>

    </div>
  );
};

export default CentersList;
