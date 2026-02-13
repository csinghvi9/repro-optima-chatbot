"use client";
import React, {
  createContext,
  useContext,
  useRef,
  useEffect,
  useState,
} from "react";
// import Cookie from "js-cookie";

type WebSocketContextType = {
  ws: WebSocket | null;
  setUpWebSocket: (token: string) => void;
  disconnectWebSocket: () => void;
  sendMessage: (message: any) => void;
  isConnected: boolean;
};

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within WebSocketProvider");
  }
  return context;
};

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnecting = useRef(false);
  const [isConnected, setIsConnected] = useState(false);

  const MAX_RETRY = 5;
  const retryCountRef = useRef(0);
  const shouldReconnectRef = useRef(false); // ✅ add
  const tokenRef = useRef<string | null>(null); // ✅ add
  const reconnectTimerRef = useRef<number | null>(null);

  const clearReconnectTimer = () => {
    if (reconnectTimerRef.current) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const setUpWebSocket = (token: string) => {
    if (!token) {
      return;
    }
    shouldReconnectRef.current = true;
    tokenRef.current = token;
    clearReconnectTimer();

    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const socket = new WebSocket(
      `${process.env.NEXT_PUBLIC_WEBSOCKET_URL}/api/assistant/ws?token=${token}`
    );
    // const socket = new WebSocket(`ws://192.168.1.32:8001/ws?token=${token}`);
    wsRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      retryCountRef.current = 0;
      clearReconnectTimer();
      socket.send(
        JSON.stringify({
          type: "login_success",
          message: "Client connected successfully!",
        })
      );
    };

    socket.onmessage = (event) => {};

    socket.onerror = (e) => {
      console.error("❌ WebSocket error:", e);
      socket.close();
    };

    socket.onclose = () => {
      console.log("⚠️ WebSocket closed");
      setIsConnected(false);
      if (!shouldReconnectRef.current) return;
      if (retryCountRef.current >= MAX_RETRY) {
        // optional: bot ko close karwa sakte ho UI side se
        return;
      }
      retryCountRef.current += 1;
      const delay = 2000 * retryCountRef.current;

      clearReconnectTimer();

      reconnectTimerRef.current = window.setTimeout(() => {
        const latestToken = tokenRef.current;
        if (latestToken && shouldReconnectRef.current) {
          setUpWebSocket(latestToken);
        }
      }, delay);
    };
  };

  const disconnectWebSocket = () => {
    // ✅ stop reconnect loops
    shouldReconnectRef.current = false;
    tokenRef.current = null;
    retryCountRef.current = 0;
    clearReconnectTimer();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  };

  const sendMessage = (message: any) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.error("🚫 Cannot send message. WebSocket not connected.");
    }
  };

  useEffect(() => {
    return () => {
      // ✅ on unmount also stop reconnect
      disconnectWebSocket();
    };
  }, []);

  return (
    <WebSocketContext.Provider
      value={{ ws: wsRef.current, setUpWebSocket,disconnectWebSocket, sendMessage, isConnected }}
    >
      {children}
    </WebSocketContext.Provider>
  );
};
