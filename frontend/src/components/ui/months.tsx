import React,{useEffect} from "react";

interface MonthYearSelectProps {
    setYear: React.Dispatch<React.SetStateAction<number>>;
    setMonth:React.Dispatch<React.SetStateAction<string>>;

}

const MonthYearSelect: React.FC<MonthYearSelectProps> = ({setYear,setMonth}) => {
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const currentMonth = months[new Date().getMonth()];
  const currentYear = new Date().getFullYear();

  // Generate: [currentYear - 2, ..., currentYear + 2]
  const years = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

  useEffect(() => {
    setMonth(currentMonth);
    setYear(currentYear);
  }, []);

  return (
    <>
      {/* Month Select */}
      <select className=" cursor-pointer border border-indira_border rounded-lg px-3 py-2 text-sm text-indira_text w-[30%] focus:outline-none" defaultValue={currentMonth} onChange={(e) => setMonth(e.target.value)}>
        {months.map((month) => (
          <option key={month}>{month}</option>
        ))}
      </select>

      {/* Year Select */}
      <select className="cursor-pointer border border-indira_border rounded-lg px-3 py-2 text-sm text-indira_text w-[30%]" defaultValue={currentYear} onChange={(e) => setYear(Number(e.target.value))}>
        {years.map((year) => (
          <option key={year}>{year}</option>
        ))}
      </select>
    </>
  );
};

export default MonthYearSelect;
