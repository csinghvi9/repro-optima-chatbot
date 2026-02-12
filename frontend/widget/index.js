import initChatbotWidget from "./ChatbotWidget";

function init() {
  initChatbotWidget();
}

// ✅ Attach globally after everything is defined
if (typeof window !== "undefined") {
  window.ChatbotWidget = { init };
}

export { init };
