import React, { useState, useEffect, useRef, ReactNode } from "react";
import BookFreeConsultation from "@/components/container/bookFreeConsultation/bookFreeConsultation";
import IVFSuccessCalculator from "@/components/container/ivfSuccessCalculator/ivfSuccessCalculator";
import { useWebSocket } from "@/app/WebSocketContext";
import BotStructureNew from "@/components/container/botStructure/boxStructureNew";
import LanguageSelection from "@/components/ui/languageSelection";
import HelloMessage from "@/components/ui/hello_message";
import Typing from "@/components/ui/typing";
import FindHospital from "@/components/container/findHospital/findHospital";
import EmotionalSupport from "@/components/container/emotionalSupport/emotionalSupport";
import CalendarMessage from "@/components/ui/calendar";
import TimeSlotsMessage from "@/components/ui/timeSlots";
import CentersList from "@/components/ui/centersList";
import IVFCalculateMessageBox from "@/components/ui/ivfCalculateMessage";
import AppointmentBookedMessage from "@/components/ui/appointmentBooked";
import LifestyleAndPreparationsProps from "@/components/ui/lifestyleAndPreparations";
import BookAppointmentMessageBox from "@/components/ui/book_appointment_button";
import EmergencyMessageBox from "@/components/ui/emergencyContact";
import LoanAndEMIBox from "@/components/ui/loanAndEMI";
import SuccessRateMessage from "@/components/ui/successRate";
import SuccessRate from "@/components/container/successRateOption/successRateOption";
import IVFStepsBox from "@/components/ui/ivfSteps";
import CostAndPackageBox from "@/components/ui/costAndPackage";
import IVFCostAndPackage from "@/components/container/ivfPackage/ivfCostAndPackage";
import { translations } from "@/components/constants/translations";
import { options } from "@/components/constants/options";
import { botMessages } from "@/components/constants/botMessage";
import UnderstandingIVF from "@/components/container/UnderstandIVF/UnderstandingIVF";
import EMIFacilities from "@/components/container/emiFacilities/emiFacilities";
import IVFQuestionBox from "@/components/ui/ivfQuestion";
import AddOnServiceBox from "@/components/ui/addServiceBox";
import FeedbackBox from "@/components/ui/feedbackBox";
import MessageVideoCarousels from "@/components/ui/videoMessage";
import LanguageChange from "@/components/ui/languageChange";
import { labelMap } from "@/components/constants/labelMap";
import ServicesOffered from "@/components/container/servicesOffered/servicesOffered";
import FrequentlyAskedQuestion from "@/components/container/frequentlyAskedQuestion/frequentlyAskedQuestion";
import FAQ from "@/components/ui/faqResponse";

type ChatbotProps = {
  newThreadID: string; // or number | null | undefined (your actual type)
  setThreadID: React.Dispatch<React.SetStateAction<string | undefined>>;
  toggleChatbot: () => void; // or proper function type
};

type RenderComponentType = (
  Component: React.ComponentType<any>,
  lang: string
) => ReactNode;

type Message = {
  type: "bot" | "user";
  content: any;
  contentType?: string;
  video_url?: any;
};

export default function Chatbot({
  newThreadID,
  setThreadID,
  toggleChatbot,
}: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedOption, setSelectedOption] = useState("");
  const { setUpWebSocket, isConnected } = useWebSocket();
  const [selectedLang, setSelectedLang] = useState<string | undefined>(
    undefined
  );
  const [showoptions, setshowoptions] = useState(true);
  const [isfeedback, setisfeedback] = useState(false);
  const [videoURLMessage, isvideoURLMessage] = useState(false);
  const [typing, setTyping] = useState(true);
  const [underdevelopementsection, isunderdevelopementsection] = useState(true);
  const [initialOptions, setinitialOptions] = useState(true);
  const [translatedOptions, setTranslatedOptions] = useState(options);
  const [showCalendar, setShowCalendar] = useState(false);
  const messageRefs = useRef<(HTMLDivElement | null)[]>([]);

  const renderComponent: RenderComponentType = (Component, lang) => (
    <Component
      selectedLang={lang}
      setMessages={setMessages}
      setTyping={setTyping}
      setThreadID={setThreadID}
      newThreadID={newThreadID}
      setSelectedOption={setSelectedOption}
      setshowoptions={setshowoptions}
    />
  );
  const baseComponentMap = {
    book_consultation: BookFreeConsultation,
    success_calculator: IVFSuccessCalculator,
    find_hospital: FindHospital,
    frequently_asked_questions: FrequentlyAskedQuestion,
    // emotional_support: EmotionalSupport,
    emi_facilities: EMIFacilities,
    success_rate: SuccessRate,
    packages: IVFCostAndPackage,
    services_offered: ServicesOffered,
    understanding_ivf: UnderstandingIVF,
  };

  const componentMap: Record<string, (lang: string) => React.ReactNode> = {};

  Object.entries(labelMap).forEach(([label, key]) => {
    const componentKey = key as keyof typeof baseComponentMap;
    const Component = baseComponentMap[componentKey];
    if (Component) {
      componentMap[label] = (lang: string) => renderComponent(Component, lang);
    }
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setTyping(false);
      setMessages([
        {
          type: "bot",
          content: (
            <LanguageSelection
              onSelect={handleLanguageSelect}
              selectedLang={selectedLang}
              newThreadID={newThreadID}
            />
          ),
        },
      ]);
      setshowoptions(true);
    }); // 2 seconds

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    const secondLastMsg = messages[messages.length - 2];
    if (lastMsg?.type === "user") {
      const lastIndex = messages.length - 1;
      const ref = messageRefs.current[lastIndex];
      if (ref) {
        ref.scrollIntoView({ behavior: "smooth" });
      }
    }

    if (lastMsg?.type === "bot" && secondLastMsg?.type === "user") {
      const lastIndex = messages.length - 1;
      const ref = messageRefs.current[lastIndex];
      if (ref) {
        ref.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messages, selectedLang]);

  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  const handleLanguageSelect = (lang: string) => {
    setSelectedLang(lang);
    setMessages((prev) => {
      const newMessages = [...prev];
      // Update first bot message with new selectedLang
      newMessages[0] = {
        type: "bot",
        content: (
          <LanguageSelection
            onSelect={handleLanguageSelect}
            selectedLang={lang}
            newThreadID={newThreadID}
          />
        ),
      };

      return [
        ...newMessages,
        { type: "user", content: lang },
        {
          type: "bot",
          content: botMessages[lang] || botMessages.en,
        },
      ];
    });

    setTranslatedOptions(translations[lang] || translations.English);
  };

  console.log(" the last message is ", messages);
  return (
    <BotStructureNew
      selectedLang={selectedLang}
      newThreadID={newThreadID}
      setSelectedLang={(lang) => handleLanguageSelect(lang)}
      messages={messages}
      setMessages={setMessages}
      setTyping={setTyping}
      setshowoptions={setshowoptions}
      setThreadID={setThreadID}
      isvideoURLMessage={isvideoURLMessage}
      isunderdevelopementsection={isunderdevelopementsection}
      setSelectedOption={setSelectedOption}
      translatedOptions={translatedOptions}
      initialOptions={initialOptions}
      setinitialOptions={setinitialOptions}
      toggleChatbot={toggleChatbot}
    >
      <div
        className={`flex flex-col flex-1 overflow-y-auto space-y-4 no-scrollbar h-full md:h-[420px] lg:h-[420px] 
    ${messages.length <= 1 ? "justify-end" : "justify-start"}`}
      >
        <HelloMessage />
        {messages.map((msg, idx) => (
          <div
            key={idx}
            ref={(el) => {
              messageRefs.current[idx] = el; // assign the ref
            }}
            className={`flex items-start w-full gap-2 ${
              msg.type === "bot" ? "justify-start" : "justify-end"
            }`}
          >
            {msg.type === "bot" ? (
              msg.contentType === "success_rate" ? (
                <div className="w-full">
                  {/* full width wrapper */}
                  <SuccessRateMessage msg={msg.content} />
                </div>
              ) : msg.contentType === "greetings" ? (
                <HelloMessage msg={msg.content} />
              ) : msg.contentType === "video_url" ? (
                <MessageVideoCarousels message={msg.content} />
              ) : msg.contentType === "add_on_service" ? (
                <div className="flex items-end gap-2 max-w-[95%]">
                  {/* Bot icon */}
                  <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                    <img
                      src="/bot_side_icon.png"
                      alt="bot"
                      className="w-[26px] h-[30px]"
                    />
                  </div>
                  <AddOnServiceBox msg={msg.content} />
                </div>
              ) : msg.contentType === "booked" ? (
                <div className="flex items-end gap-2 max-w-[95%]">
                  {/* Bot icon */}
                  <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                    <img
                      src="/bot_side_icon.png"
                      alt="bot"
                      className="w-[26px] h-[30px]"
                    />
                  </div>
                  <AppointmentBookedMessage msg={msg} />
                </div>
              ) : msg.contentType === "frequently_asked_questions" ? (
                <div className="flex items-end gap-2 max-w-[95%]">
                  {/* Bot icon */}
                  <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                    <img
                      src="/bot_side_icon.png"
                      alt="bot"
                      className="w-[26px] h-[30px]"
                    />
                  </div>
                  <FAQ msg={msg.content} />
                </div>
              ) : (
                <div className="flex items-end gap-2 max-w-[80%]">
                  {/* Bot icon */}
                  {/* <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                    <img
                      src="/bot_side_icon.png"
                      alt="bot"
                      className="w-[26px] h-[30px]"
                    />
                  </div> */}
                  {!messages[idx + 1] ||
                  messages[idx + 1].type !== "bot" ||
                  (messages[idx + 1] &&
                    messages[idx + 1].contentType === "video_url" &&
                    messages[idx].type === "bot") ? (
                    <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                      <img
                        src="/bot_side_icon.png"
                        alt="bot"
                        className="w-[26px] h-[30px]"
                      />
                    </div>
                  ) : (
                    <div className="w-8 h-8" /> // Empty placeholder for alignment
                  )}

                  {/* Typing animation */}
                  {typing && msg.content === "typing" ? (
                    <Typing />
                  ) : (
                    msg.content !== "typing" &&
                    (React.isValidElement(msg.content) ? (
                      <div>{msg.content}</div>
                    ) : msg.contentType ? (
                      msg.contentType === "centers" ? (
                        <CentersList
                          centers={
                            Array.isArray(msg.content) ? msg.content : []
                          }
                          onSelect={(city) => {
                            if (city)
                              setMessages((prev) => [
                                ...prev,
                                { type: "user", content: city },
                              ]);
                          }}
                          newThreadID={newThreadID}
                          setTyping={setTyping}
                          messages={messages}
                        />
                      ) : msg.contentType === "calendar" ? (
                        <CalendarMessage
                          text={msg.content}
                          newThreadID={newThreadID}
                          setTyping={setTyping}
                          showCalendar={showCalendar}
                          setShowCalendar={setShowCalendar}
                          onSelectDate={(date) => {
                            if (date)
                              setMessages((prev) => [
                                ...prev,
                                { type: "user", content: date },
                              ]);
                          }}
                        />
                      ) : msg.contentType === "time_slots" ? (
                        <div className="bg-white text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%]">
                          {msg.content}
                        </div>
                      ) : msg.contentType === "Lifestyle_and_Preparations" ? (
                        <LifestyleAndPreparationsProps msg={msg.content} />
                      ) : msg.contentType === "ivf_calculate" ? (
                        <IVFCalculateMessageBox
                          msg={msg.content}
                          newThreadID={newThreadID}
                          setTyping={setTyping}
                        />
                      ) : msg.contentType === "book_appointment" ? (
                        <BookAppointmentMessageBox
                          msg={msg.content}
                          newThreadID={newThreadID}
                          setTyping={setTyping}
                          setMessages={setMessages}
                          selectedLang={selectedLang}
                          setThreadID={setThreadID}
                          setSelectedOption={setSelectedOption}
                          setshowoptions={setshowoptions}
                        />
                      ) : // : msg.contentType === "booked" ? (
                      //   <AppointmentBookedMessage msg={msg} />
                      // )
                      msg.contentType === "loan_and_emi" ? (
                        <LoanAndEMIBox
                          msg={msg.content?.content}
                          newThreadID={newThreadID}
                        />
                      ) : msg.contentType === "ivf_steps" ? (
                        <IVFStepsBox msg={msg.content} />
                      ) : msg.contentType === "feedback" ? (
                        <FeedbackBox
                          msg={msg.content}
                          setisfeedback={setisfeedback}
                          newthreadId={newThreadID}
                        />
                      ) : msg.contentType === "cost_and_package" ? (
                        <CostAndPackageBox msg={msg.content} />
                      ) : msg.contentType === "language_change" ? (
                        <LanguageChange
                          onSelect={handleLanguageSelect}
                          selectedLang={selectedLang}
                          newThreadID={newThreadID}
                          setTyping={setTyping}
                        />
                      ) : msg.contentType === "ivf_question" ? (
                        <IVFQuestionBox msg={msg.content} />
                      ) : msg.contentType === "whats_app" ? (
                        <EmergencyMessageBox msg={msg.content} />
                      ) : msg.contentType === "emotional_support" ? (
                        (() => {
                          const content = msg.content;
                          const phoneNumberMatch = content.match(/(\d{10,})/);
                          const phoneNumber = phoneNumberMatch
                            ? phoneNumberMatch[0]
                            : "";

                          const textBeforeNumber = content.replace(
                            /[-–—]?\s*\d{10,}.*/,
                            ""
                          );

                          return (
                            <div className="bg-white px-3 py-2 rounded text-xs font-indira_font text-indira_text max-w-[75%]">
                              <p className="text-indira_hover_text">
                                {textBeforeNumber.trim()}
                              </p>
                              {phoneNumber && (
                                <p className="text-indira_text font-indira_font font-semibold text-base mt-1">
                                  {phoneNumber}
                                </p>
                              )}
                            </div>
                          );
                        })()
                      ) : msg.contentType === "emergency_contact" ? (
                        typeof msg.content === "object" ? (
                          <div className="bg-white font-indira_font text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%] flex flex-col">
                            <span className="text-xs text-indira_text font-indira_font font-normal">
                              {msg.content?.heading}
                            </span>
                            <span className="text-[16px] text-indira_text font-indira_font font-semibold">
                              {msg.content?.phone_number}
                            </span>
                            <span className="text-xs text-indira_hover_text font-indira_font font-normal mt-2">
                              {msg.content?.text}
                            </span>
                          </div>
                        ) : (
                          <EmergencyMessageBox msg={msg.content} />
                        )
                      ) : msg.contentType === "out_of_context" ? (
                        <div className="bg-white font-indira_font text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%] flex flex-col">
                          <span className="text-xs text-indira_hover_text font-indira_font font-normal">
                            {msg.content?.first_text}
                          </span>
                          <span className="text-xs text-indira_text font-indira_font font-normal mt-2">
                            {msg.content?.second_text}
                          </span>
                          <span className="text-[16px] text-indira_text font-indira_font font-semibold mt-2">
                            {msg.content?.phone_number}
                          </span>
                        </div>
                      ) : (
                        <div
                          className="bg-white font-indira_font text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%]"
                          style={{ whiteSpace: "pre-line" }}
                        >
                          {msg.content}
                        </div>
                      )
                    ) : (
                      <div
                        className="bg-white font-indira_font text-indira_text px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs max-w-[75%]"
                        style={{ whiteSpace: "pre-line" }}
                      >
                        {msg.content}
                      </div>
                    ))
                  )}
                </div>
              )
            ) : null}
            {msg.type === "user" && (
              <div className="flex items-end gap-2 max-w-[65%]">
                <div className="bg-indira_user_message_bg text-indira_text px-2 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-bl-[10px] rounded-br-[4px] text-xs font-indira_font  ">
                  {msg.content}
                </div>
              </div>
            )}
          </div>
        ))}
        {typing && (
          <div className="flex items-start gap-2 justify-start">
            <div className="w-[32px] h-[32px] rounded-full bg-white flex items-center justify-center mt-[5px]">
              <img
                src="/bot_side_icon.png"
                alt="bot icon"
                className="w-[26px] h-[30px]"
              />
            </div>
            <Typing />
          </div>
        )}
        {messages[messages.length - 1]?.contentType === "time_slots" && (
          <TimeSlotsMessage
            newThreadID={newThreadID}
            setTyping={setTyping}
            onSelectTimeSlot={(time) => {
              if (time)
                setMessages((prev) => [
                  ...prev,
                  { type: "user", content: time },
                ]);
            }}
            previousMessages={messages}
          />
        )}
        {selectedLang && !selectedOption && showoptions && initialOptions && (
          <div className="flex flex-wrap gap-2">
            {translatedOptions.map((opt, i) => (
              <button
                key={i}
                className="border border-indira_dark_red text-indira_text font-normal font-indira_font text-xs px-[8px] py-[4px] rounded-full hover:text-indira_hover_text transition"
                onClick={() => {
                  setSelectedOption(opt);
                  setinitialOptions(false);
                }}
              >
                {opt}
              </button>
            ))}
          </div>
        )}
        {isConnected && selectedOption && (
          <div className="mt-4">
            {componentMap[selectedOption] ? (
              selectedLang ? (
                componentMap[selectedOption](selectedLang)
              ) : (
                componentMap[selectedOption]("English")
              )
            ) : (
              //   componentMap[selectedOption](selectedLang) // Pass language here
              <>
                {underdevelopementsection && (
                  <>
                    <p className="text-sm text-gray-500">
                      This section is under development.
                    </p>
                  </>
                )}
              </>
            )}
          </div>
        )}
        <span></span>
      </div>
    </BotStructureNew>
  );
}
