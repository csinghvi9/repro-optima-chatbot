// import type { NextConfig } from "next";

// const nextConfig: NextConfig = {

//   reactStrictMode: false,

//   eslint: {
//     ignoreDuringBuilds: true,
//   },
// };

// export default nextConfig;
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: false,

  eslint: {
    ignoreDuringBuilds: true,
  },

  async headers() {
    return [
      {
        source: "/widget/:path*", // ✅ Matches all widget files (e.g., chatbot.bundle.js)
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" }, // Allow all origins (or use specific domain)
          { key: "Access-Control-Allow-Methods", value: "GET, OPTIONS" },
          { key: "Access-Control-Allow-Headers", value: "Content-Type" },
        ],
      },
    ];
  },
};

export default nextConfig;
