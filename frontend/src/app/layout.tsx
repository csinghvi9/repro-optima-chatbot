import type { Metadata } from "next";
import { Open_Sans,Quicksand } from "next/font/google";
import { WebSocketProvider } from '@/app/WebSocketContext';
import "./globals.css";
import Script from 'next/script';

const openSans = Open_Sans({
  variable: "--font-open-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"], // choose weights as needed
});
const quicksand = Quicksand({
  variable: "--font-qui",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "IVF Bot",
  description: "IVF Bot – your smart assistant for seamless IVF guidance, support, and care.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${openSans.variable} ${quicksand.variable}`}>
      <head>
        {/* 👇 Explicitly force the viewport meta tag */}
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"     
        />
        <title>IVF Bot</title>
        <link rel="icon" href="/bot_logo.ico" />
      </head>
      <body>
        <WebSocketProvider>
          {children}
        </WebSocketProvider>
        {/* <Script
          src={`https://maps.googleapis.com/maps/api/js?key=AIzaSyDxKlLbMwU6Ue8XS6ATVDncUMkQsCRNbIA`}
          async
          defer
        /> */}
      </body>
    </html>
  );
}
