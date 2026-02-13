// export default function initChatbotWidget() {
//   if (document.getElementById("iivf-chatbot-frame")) return;

//   const style = document.createElement("style");
//   style.textContent = `
//     @media (max-width: 767px) {
//       iframe#iivf-chatbot-frame {
//         z-index: 1000 !important;
//         height: 100% !important;
//         bottom: unset !important;
//         top: 0 !important;
//       }
//     }
//   `;
//   document.head.appendChild(style);

//   const iframe = document.createElement("iframe");
//   iframe.id = "iivf-chatbot-frame";
//   iframe.src = "https://iivf-chatbot-dev-frontend-tg.meddilink.com/";
//   iframe.allow = "fullscreen; microphone; clipboard-write";
//   iframe.allowTransparency = "true";
//   iframe.style.cssText = `
//     position: fixed;
//     inset: 0px;
//     width: fit-content;
//     height: fit-content;
//     border: none;
//     background: transparent;
//     z-index: 999999;
//     pointer-events: auto;
//     display: block;
//     overscroll-behavior: contain;
//     right: 0;
//     left: unset;
//     bottom: 0;
//     top: unset
//   `;

//   // Ensures iOS Safari and Android Chrome respect full viewport height
//   iframe.setAttribute("allowfullscreen", "true");
//   iframe.setAttribute("frameBorder", "0");

//   document.body.appendChild(iframe);
//   window.addEventListener("message", (event) => {
//     if (event.origin !== "https://iivf-chatbot-dev-frontend-tg.meddilink.com") return;

//     const { type } = event.data;

//     if (type === "CHATBOT_OPEN") {
//       iframe.style.width = "30vw";
//       iframe.style.height = "90vh";
//     }

//     if (type === "CHATBOT_CLOSE") {
//       iframe.style.width = "fit-content";
//       iframe.style.height = "fit-content";
//     }
//   });
// }

export default function initChatbotWidget() {
  if (document.getElementById("iivf-chatbot-frame")) return;

  /* -------------------- Inject CSS -------------------- */
  const style = document.createElement("style");
  style.textContent = `
    .chat-boat-wrap {
      opacity: 1;
      visibility: visible;
      z-index: 2;
      position: fixed;
      bottom: 10px;
      right: 10px;
      width: 233px;
      height: 169px;
      max-width: 100%;
      max-height: calc(100% + 0px);
      min-height: 0;
      min-width: 0;
    }

    .chat-boat-wrap iframe#iivf-chatbot-frame {
      width: 100%;
      height: 100%;
      background: transparent;
      pointer-events: auto;
      border: none;
      border-radius: 16px;
    }

    /* ---------------- OPEN STATE ---------------- */
    .chat-boat-wrap.open {
      width: 420px;
      height:85vh;
      right:10px;
      border: none;
      bottom: 10px;
    }

    .chat-boat-wrap.open iframe#iivf-chatbot-frame {
      width: 100%;
      height: 100%;
      background: transparent;
      pointer-events: auto;
      border: none;
      border-radius: 16px;
    }

    /* ---------------- MOBILE ---------------- */
    @media (max-width: 767px) {
      .chat-boat-wrap {
    position: fixed;
    bottom: 0;
    width:fit-content; 
    height:fit-content;
    z-index: 1000;
  }
    .chat-boat-wrap iframe#iivf-chatbot-frame {
      height: 105px;
      width:120px;
      position: fixed;
      bottom:9%;
      right:10px;
    }
  .chat-boat-wrap.open{
    width: 100%;
    height: 100%;
    display: block;
    position: fixed;
    bottom:0;
    right:0;
  }

  .chat-boat-wrap.open iframe#iivf-chatbot-frame {
    width: 100%;
    height: 100%;
    display: block;
    position: fixed;
    bottom:0;
    right:0;
    border-radius:0;
  }
    }
  `;
  document.head.appendChild(style);

  /* -------------------- Wrapper -------------------- */
  const wrapper = document.createElement("div");
  wrapper.className = "chat-boat-wrap";

  /* -------------------- Iframe -------------------- */
  const iframe = document.createElement("iframe");
  iframe.id = "iivf-chatbot-frame";
  iframe.src = "https://iivfchatbot.indiraivf.com/";
  iframe.allow = "fullscreen; microphone; clipboard-write; geolocation";
  iframe.setAttribute("allowfullscreen", "true");
  iframe.setAttribute("frameBorder", "0");

  wrapper.appendChild(iframe);
  document.body.appendChild(wrapper);

  let closeTimeout = null;

  /* -------------------- PostMessage Listener -------------------- */
  window.addEventListener("message", (event) => {
    const allowedOrigins = [
      "https://iivfchatbot.indiraivf.com",
      "https://iivf-chatbot-dev-frontend-tg.meddilink.com",
    ];

    if (!allowedOrigins.includes(event.origin)) return;

    const { type } = event.data;

    if (type === "CHATBOT_OPEN") {
      // 🔥 agar koi close pending hai to cancel
      if (closeTimeout) {
        clearTimeout(closeTimeout);
        closeTimeout = null;
      }

      wrapper.classList.add("open");
    }

    if (type === "CHATBOT_CLOSE") {
      // 🔥 overwrite previous timeout
      if (closeTimeout) {
        clearTimeout(closeTimeout);
      }

      closeTimeout = setTimeout(() => {
        wrapper.classList.remove("open");
        closeTimeout = null;
      }, 500);
    }
  });
}
