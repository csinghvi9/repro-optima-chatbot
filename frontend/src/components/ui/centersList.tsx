import React, { useEffect, useState } from "react";
import { useWebSocket } from "@/app/WebSocketContext";

interface Center {
  "Clinic Name": string;
  Distance_km: number | string;
  [key: string]: any; // in case extra fields come
}
declare global {
  interface Window {
    google: any;
  }
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
  // const [showMapModal, setShowMapModal] = useState(false);
  // const [userCoords, setUserCoords] = useState<{
  //   lat: number;
  //   lng: number;
  // } | null>(null);
  // const [centerCoords, setCenterCoords] = useState<{
  //   lat: number;
  //   lng: number;
  // } | null>(null);
  // const [selectedCenter, setSelectedCenter] = useState<Center | null>(null);

  // 🗺️ Initialize map when modal opens
  // useEffect(() => {
  //   if (showMapModal && window.google && selectedCenter) {
  //     const geocoder = new window.google.maps.Geocoder();
  //     const fallbackCoords = { lat: 28.6139, lng: 77.209 }; // New Delhi fallback

  //     // Get user's location
  //     navigator.geolocation.getCurrentPosition(
  //       (pos) => {
  //         const coords = {
  //           lat: pos.coords.latitude,
  //           lng: pos.coords.longitude,
  //         };
  //         setUserCoords(coords);
  //         initMap(coords);
  //       },
  //       (error) => {
  //         console.warn("Geolocation failed, using fallback:", error);
  //         setUserCoords(fallbackCoords);
  //         initMap(fallbackCoords);
  //       }
  //     );

  //     // Initialize map
  //     const initMap = (userLocation: { lat: number; lng: number }) => {
  //       geocoder.geocode(
  //         { address: selectedCenter.Address },
  //         (results: any, status: string) => {
  //           let clinicCoords = fallbackCoords;

  //           if (status === "OK" && results[0]) {
  //             clinicCoords = {
  //               lat: results[0].geometry.location.lat(),
  //               lng: results[0].geometry.location.lng(),
  //             };
  //             setCenterCoords(clinicCoords);
  //           }

  //           const map = new window.google.maps.Map(
  //             document.getElementById("map") as HTMLElement,
  //             {
  //               center: clinicCoords,
  //               zoom: 11,
  //             }
  //           );

  //           // 🧍 User Marker
  //           new window.google.maps.Marker({
  //             position: userLocation,
  //             map,
  //             label: { text: "You", color: "white" },
  //             icon: {
  //               path: window.google.maps.SymbolPath.CIRCLE,
  //               scale: 6,
  //               fillColor: "#007AFF",
  //               fillOpacity: 1,
  //               strokeWeight: 1,
  //               strokeColor: "#fff",
  //             },
  //           });

  //           // 🏥 Clinic Marker
  //           new window.google.maps.Marker({
  //             position: clinicCoords,
  //             map,
  //             label: { text: "Clinic", color: "white" },
  //             icon: {
  //               url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
  //             },
  //           });

  //           // Adjust map to show both markers
  //           const bounds = new window.google.maps.LatLngBounds();
  //           bounds.extend(userLocation);
  //           bounds.extend(clinicCoords);
  //           map.fitBounds(bounds);
  //         }
  //       );
  //     };
  //   }
  // }, [showMapModal, selectedCenter]);
  const [mapsUrl, setMapsUrl] = useState("");

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

  const handleOpenMapDirection = (centerName: string) => {
    const destination = encodeURIComponent(centerName);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${latitude},${longitude}&destination=${destination}`;
          window.open(mapsUrl, "_blank");
        },
        (error) => {
          if (error.code === error.PERMISSION_DENIED) {
            // open settings again if denied
            window.open("chrome://settings/content/location", "_blank");
          } else {
            console.error("Geolocation error:", error.message);
          }
        }
      );
    } else {
      alert("Your browser does not support location services.");
    }
  };

  return (
    <div className="bg-white px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[80%]">
      <p className="text-indira_text mb-2 text-xs">
        Here are the nearby centers:
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
              const lastMessage = messages[messages.length - 1];
              const isCentersContent = lastMessage?.contentType === "centers";

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
                          className={`text-indira_dark_red font-semibold ${
                            isCentersContent
                              ? "cursor-pointer hover:underline"
                              : "cursor-default"
                          }`}
                          onClick={() => {
                            if (!isCentersContent) return;
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
                            handleOpenMapDirection(center["Clinic Name"]);
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
        Click on the center’s name to view the complete address, or use the map
        icon to view its location.
      </p>

      {/* 🗺️ Map Modal */}
      {/* {showMapModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
          <div className="bg-white p-4 rounded-xl w-[90%] max-w-lg relative">
            <button
              className="absolute top-2 right-2 text-gray-500 text-sm cursor-pointer"
              onClick={() => setShowMapModal(false)}
            >
              ✕
            </button>
            <h3 className="text-sm font-semibold mb-2 text-gray-800">
              {selectedCenter?.["Clinic Name"]}
            </h3>
            <div id="map" className="w-full h-[400px] rounded-md"></div>
          </div>
        </div>
      )} */}
    </div>
  );
};

export default CentersList;
