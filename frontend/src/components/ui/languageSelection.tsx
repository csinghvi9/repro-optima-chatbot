import React from "react";
import useThreads from '@/components/threads/threads.hook'

interface LanguageSelectionProps {
  onSelect: (lang: string) => void;
  selectedLang?: string;
  newThreadID: string;
}

const LanguageSelection: React.FC<LanguageSelectionProps> = ({ onSelect, selectedLang,newThreadID }) => {

  const { changeLanguage } = useThreads();
  const languages: string[] = [
    "English",
    "हिन्दी",
    "मराठी",
    "ગુજરાતી",
    "ಕನ್ನಡ",
    "বাংলা",
    "தமிழ்",
    "ਪੰਜਾਬੀ",
    "অসমীয়া",
    "ଓଡ଼ିଆ",
    "తెలుగు"
  ];
  const handleChangeLanguage = async (lang: string) => {

      if (newThreadID){

        await changeLanguage(newThreadID, lang);
      }
       onSelect(lang)
    };
  return (
    <div className="border border-indira_hello_border bg-white px-3 py-2 rounded-tl-[10px] rounded-tr-[10px] rounded-br-[10px] rounded-bl-[4px] flex flex-col gap-2 max-w-[80%] h-[212px]">
      <p className="text-[12px] text-indira_text">
        Please select your preferred Language
      </p>

      <div className="overflow-y-auto customScrollbar flex flex-col  gap-2 focus:outline-none">
        {languages.map((lang) => (
          <div
            key={lang}
            onClick={() => handleChangeLanguage(lang)}
            className={`px-3 py-1 rounded-full text-[12px] font-indira_font cursor-pointer text-center w-[90%] ${
              lang === selectedLang
                ? "bg-gradient-to-br from-indira_light_red to-indira_dark_red text-white"
                : "bg-red-50 text-indira_dark_red border border-red-200"
            }`}
          >
            {lang}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LanguageSelection;
