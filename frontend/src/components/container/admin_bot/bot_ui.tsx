import React, { useState, useEffect } from "react";
import BotStructure from "@/components/ui/bot_structure";
import HelloMessage from "@/components/ui/hello_message";
import CentersList from "@/components/ui/centersList";
import IVFCalculateMessageBox from "@/components/ui/ivfCalculateMessage";
import AppointmentBookedMessage from "@/components/ui/appointmentBooked";
import LifestyleAndPreparationsProps from "@/components/ui/lifestyleAndPreparations";
import BookAppointmentMessageBox from "@/components/ui/book_appointment_button";
import EmergencyMessageBox from "@/components/ui/emergencyContact";
import LoanAndEMIBox from "@/components/ui/loanAndEMI";
import SuccessRateMessage from "@/components/ui/successRate";
import IVFStepsBox from "@/components/ui/ivfSteps";
import CostAndPackageBox from "@/components/ui/costAndPackage";
import IVFQuestionBox from "@/components/ui/ivfQuestion";
import AddOnServiceBox from "@/components/ui/addServiceBox";
import FeedbackBox from "@/components/ui/feedbackBox";
import MessageVideoCarousels from "@/components/ui/videoMessage";
import LanguageSelection from "@/components/ui/languageSelection";
import LanguageChange from "@/components/ui/languageChange";
import FAQ from "@/components/ui/faqResponse";

const BotAvatar = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-[22px] h-[22px]">
    <rect x="3" y="8" width="18" height="13" rx="5" fill="#CE3149"/>
    <circle cx="9" cy="14" r="1.5" fill="white"/>
    <circle cx="15" cy="14" r="1.5" fill="white"/>
    <path d="M10 17.5C11 18.8 13 18.8 14 17.5" stroke="white" strokeWidth="1.2" strokeLinecap="round"/>
    <line x1="12" y1="8" x2="12" y2="5" stroke="#CE3149" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="12" cy="3.5" r="1.8" fill="#CE3149"/>
  </svg>
);

type Message = {
  role: "bot" | "user";
  content: any;
  contentType?: string;
  video_url?: any;
};

type Thread = {
  _id: string;
  language: string;
  messages: Message[];
};

type ChatbotProps = {
  setBotUI: React.Dispatch<React.SetStateAction<boolean>>;
  thread: Thread | null; // or number | null | undefined (your actual type)
};

export default function BOTUI({ setBotUI, thread }: ChatbotProps) {
  useEffect(() => {
    if (window.innerWidth < 768) {
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);
  const messages = thread?.messages ?? [];
  const newThreadID = thread?._id ?? "";
  const selectedLang = thread?.language ?? "English";
  const [videoURLMessage, isvideoURLMessage] = useState(false);
  const handleLanguageSelect = async (lang: string) => {
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div
        className="relative bg-white shadow-lg border border-gray-300 
                  w-full h-full md:w-[50vw] md:h-[90vh] lg:w-[30vw] lg:h-[80vh] md:rounded-2xl overflow-hidden 
                  flex flex-col items-center "
      >
        <BotStructure setBotUI={setBotUI}>
          <div
            className={`flex flex-col flex-1 overflow-y-auto space-y-4 no-scrollbar h-full 
    ${messages.length <= 1 ? "justify-end" : "justify-start"}`}
          >
            <HelloMessage />
            <div className="flex items-end gap-2 max-w-[70%]">
              <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                <BotAvatar />
              </div>
              <LanguageSelection
                onSelect={handleLanguageSelect}
                selectedLang={selectedLang}
                newThreadID={newThreadID}
              />
            </div>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex items-start w-full gap-2 ${
                  msg.role === "bot" ? "justify-start" : "justify-end"
                }`}
              >
                {msg.role === "bot" ? (
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
                        <BotAvatar />
                      </div>
                      <AddOnServiceBox msg={msg.content} />
                    </div>
                  ) : msg.contentType === "booked" ? (
                    <div className="flex items-end gap-2 max-w-[95%]">
                      {/* Bot icon */}
                      <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                        <BotAvatar />
                      </div>
                      <AppointmentBookedMessage msg={msg} />
                    </div>
                  ) : msg.contentType === "frequently_asked_questions" ? (
                    <div className="flex items-end gap-2 max-w-[95%]">
                      {/* Bot icon */}
                      <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                        <BotAvatar />
                      </div>
                      <FAQ msg={msg.content} />
                    </div>
                  ) : (
                    <div className="flex items-end gap-2 max-w-[80%]">
                      {!messages[idx + 1] ||
                      messages[idx + 1].role !== "bot" ||
                      (messages[idx + 1] &&
                        messages[idx + 1].contentType === "video_url" &&
                        messages[idx].role === "bot") ? (
                        <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
                          <BotAvatar />
                        </div>
                      ) : (
                        <div className="w-8 h-8" /> // Empty placeholder for alignment
                      )}
                      {msg.content !== "typing" &&
                        (React.isValidElement(msg.content) ? (
                          <div>{msg.content}</div>
                        ) : msg.contentType ? (
                          msg.contentType === "centers" ? (
                            <CentersList
                              centers={
                                Array.isArray(msg.content) ? msg.content : []
                              }
                              onSelect={(city) => {}}
                              newThreadID={newThreadID}
                            />
                          ) : msg.contentType ===
                            "Lifestyle_and_Preparations" ? (
                            <LifestyleAndPreparationsProps msg={msg.content} />
                          ) : msg.contentType === "ivf_calculate" ? (
                            <IVFCalculateMessageBox
                              msg={msg.content}
                              newThreadID={newThreadID}
                            />
                          ) : msg.contentType === "book_appointment" ? (
                            <BookAppointmentMessageBox
                              msg={msg.content}
                              newThreadID={newThreadID}
                              selectedLang={selectedLang}
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
                              newthreadId={newThreadID}
                            />
                          ) : msg.contentType === "cost_and_package" ? (
                            <CostAndPackageBox msg={msg.content} />
                          ) : msg.contentType === "langugae_change" ? (
                            <LanguageChange
                              onSelect={handleLanguageSelect}
                              selectedLang={selectedLang}
                              newThreadID={newThreadID}
                            />
                          ) : msg.contentType === "ivf_question" ? (
                            <IVFQuestionBox msg={msg.content} />
                          ) : msg.contentType === "whats_app" ? (
                            <EmergencyMessageBox msg={msg.content} />
                          ) : msg.contentType === "emotional_support" ? (
                            (() => {
                              const content = msg.content;
                              const phoneNumberMatch =
                                content.match(/(\d{10,})/);
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
                        ))}
                    </div>
                  )
                ) : null}
                {msg.role === "user" && (
                  <div className="flex items-end gap-2 max-w-[65%]">
                    <div className="bg-indira_user_message_bg text-indira_text px-2 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-bl-[10px] rounded-br-[4px] text-xs font-indira_font  ">
                      {msg.content}
                    </div>
                  </div>
                )}
              </div>
            ))}

            <span></span>
          </div>
        </BotStructure>
      </div>
    </div>
  );
}
