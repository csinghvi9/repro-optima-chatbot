import React from "react";
import VideoModalPlayer from "@/components/ui/videoPlayer";


interface VideoMessage {
  video_url: string;
  thumbnail_url: string;
  heading:string
  description:string
}

interface MessageVideoCarouselsProps {
  message: VideoMessage[];
}

const MessageVideoCarousels: React.FC<MessageVideoCarouselsProps> = ({ message }) => {
  return (
    <div className="w-full max-w-full flex overflow-x-auto overflow-y-hidden gap-2 horizontalcustomScrollbar">
      {message.map((url, index) => (
        <div
          key={index}
          className="flex-shrink-0 w-[30%] h-[95%] rounded-[12px] cursor-pointer"
        >
          <VideoModalPlayer url={url} />
        </div>
      ))}
    </div>
  );
};

export default MessageVideoCarousels;
