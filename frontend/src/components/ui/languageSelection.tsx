import React from "react";
import useThreads from '@/components/threads/threads.hook'

interface LanguageSelectionProps {
  onSelect: (lang: string) => void;
  selectedLang?: string;
  newThreadID: string;
}

const LanguageSelection: React.FC<LanguageSelectionProps> = ({ onSelect, selectedLang, newThreadID }) => {

  const { changeLanguage } = useThreads();
  const languages: { label: string; flag: string }[] = [
    { label: "English", flag: "🇬🇧" },
    { label: "Русский", flag: "🇷🇺" },
    { label: "Filipino", flag: "🇵🇭" },
  ];

  const handleChangeLanguage = async (lang: string) => {
    if (newThreadID) {
      await changeLanguage(newThreadID, lang);
    }
    onSelect(lang);
  };

  return (
    <div className="bg-white border border-indira_hello_border px-4 py-3 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] flex flex-col gap-3 max-w-[100%]">
      <p className="text-xs font-medium text-indira_text">
        Please select your preferred Language
      </p>
      <div className="flex flex-row gap-2">
        {languages.map((lang) => (
          <button
            key={lang.label}
            onClick={() => handleChangeLanguage(lang.label)}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-indira_font cursor-pointer transition-all ${
              lang.label === selectedLang
                ? "bg-gradient-to-br from-indira_light_red to-indira_dark_red text-white shadow-sm"
                : "bg-red-50 text-indira_dark_red border border-red-200 hover:bg-red-100"
            }`}
          >
            <span className="text-sm">{lang.flag}</span>
            {lang.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default LanguageSelection;
