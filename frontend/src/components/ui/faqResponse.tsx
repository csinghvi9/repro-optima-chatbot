import React, { useState } from "react";

interface FAQItem {
  question: string;
  answer: string;
}

type FAQMessage = FAQItem | string;

interface FAQProps {
  msg: FAQMessage[];
  title?: string;
  defaultOpenIndex?: number | null;
}

const ChevronDownIcon = ({ rotated }: { rotated: boolean }) => (
  <svg
    className={`h-5 w-5 transition-transform duration-200 ${
      rotated ? "rotate-180" : ""
    }`}
    viewBox="0 0 24 24"
    fill="none"
    aria-hidden="true"
  >
    <path
      d="M6 9l6 6 6-6"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const FAQ: React.FC<FAQProps> = ({ msg, defaultOpenIndex = null }) => {
  const [openIndex, setOpenIndex] = useState<number | null>(defaultOpenIndex);

  // ✅ Separate FAQs and notes
  const faqItems = msg.filter(
    (item): item is FAQItem => typeof item === "object"
  );

  const notes = msg.filter(
    (item): item is string => typeof item === "string"
  );

  const toggle = (index: number) => {
    setOpenIndex((prev) => (prev === index ? null : index));
  };

  return (
    <div className="bg-white ml-1 md:ml-0 text-indira_text rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] text-xs w-full whitespace-pre-line pl-4 py-4 pr-2">
      {/* FAQ Accordion */}
      <div className="divide-y divide-black/10">
        {faqItems.map((item, index) => {
          const isOpen = openIndex === index;
          const panelId = `faq-panel-${index}`;

          return (
            <div key={index} className="py-2">
              <button
                type="button"
                onClick={() => toggle(index)}
                className="w-full flex items-center justify-between gap-4 pb-2 text-left"
                aria-expanded={isOpen}
                aria-controls={panelId}
              >
                <span className="text-xs font-semibold">
                  <span>Q.</span> {item.question}
                </span>

                <span className="text-black/60">
                  <ChevronDownIcon rotated={isOpen} />
                </span>
              </button>

              <div
                id={panelId}
                className={`overflow-hidden transition-all duration-300 ${
                  isOpen ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
                }`}
              >
                <div className="pb-5 text-sm text-indira_hover_text whitespace-pre-line">
                  {item.answer}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* ✅ Notes Section (Strings at Bottom) */}
      {notes.length > 0 && (
        <div className="text-xs text-indira_hover_text">
          {notes.map((note, idx) => (
            <p key={idx} className="mt-2">
              {note}
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default FAQ;
