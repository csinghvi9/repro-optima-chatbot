import { useState, useRef } from "react";

interface URL {
  video_url: string;
  thumbnail_url: string;
  heading:string
  description:string
}

interface VideoModalPlayerProps {
  url: URL;
}

export default function VideoModalPlayer({ url }: VideoModalPlayerProps) {
  const [open, setOpen] = useState<boolean>(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const handleOpen = () => {
    setOpen(true);
    // Delay to ensure modal is rendered before playing
    setTimeout(() => {
      videoRef.current?.play().catch(() => {
        console.warn("Autoplay prevented by browser");
      });
    }, 50);
  };

  const handleClose = () => {
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0; // reset playback
    }
    setOpen(false);
  };
  return (
    <div className="w-full h-full">
      {/* 🎬 Button or thumbnail */}

      <button
        onClick={handleOpen}
        className="relative w-full h-full rounded-[12px] overflow-hidden cursor-pointer"
      >
        {/* Video / Thumbnail */}
        <video
          src={url.video_url}
          poster={url.thumbnail_url}
          className="w-full h-full rounded-[12px] object-cover"
          muted
          playsInline
          preload="auto"
        />

        {/* Dark gradient overlay (bottom 40%) */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent">
        <div className="relative h-[70%] md:h-[80%] inset-0 flex items-center justify-center">
          <div className="bg-black/50 rounded-full p-4 shadow-lg">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>

        {/* Bottom text */}
        <div className=" text-white z-20 w-full h-[30%] md:h-[20%]">
          <p className="text-xs font-semibold block overflow-hidden truncate whitespace-nowrap pl-1">{url.heading}</p>
          <p className="text-[8px]  block overflow-hidden truncate whitespace-nowrap pl-1">
            {url.description}
          </p>
        </div>
        </div>
      </button>

      {/* 🪟 Modal */}
      {open && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/60 backdrop-blur-sm">
          <div className="bg-black rounded-2xl overflow-hidden w-[80%] md:w-[50%] h-[50%] relative shadow-2xl">
            <video
              ref={videoRef}
              src={url.video_url}
              className="w-full h-full object-contain"
              controls
            />
            {/* ✕ Close Button */}
            <button
              onClick={handleClose}
              className="absolute top-3 right-3 text-white rounded-full px-3 py-1 text-lg cursor-pointer"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
