"use client";
import React, { useState, useEffect } from "react";
import MonthYearSelect from "@/components/ui/months";
import BOTUI from "@/components/container/admin_bot/bot_ui";

import useThreads from "@/components/threads/threads.hook";

const Dashboard: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [month, setMonth] = useState<string>(months[new Date().getMonth()]);
  const { fetchThreads } = useThreads();
  const getMonthNumber = (name: string) => months.indexOf(name) + 1;
  const [botui, setBotUI] = useState<boolean>(false);
  const [selectedThread, setSelectedThread] = useState(null);
  const [thread_id, setthread_id] = useState("");

  useEffect(() => {
    const monthNumber = getMonthNumber(month);
    if (thread_id ===""){
    const loadData = async () => {
      const result = await fetchThreads(monthNumber, year);
      setData(result?.threads || []);
    };
    loadData();
  }
  else{
    const loadData = async () => {
      const result = await fetchThreads(monthNumber, year,thread_id);
      setData(result?.threads || []);
    };
    loadData();
  }
  }, [month, year,thread_id]);
  const formatDate = (timestamp: string) => {
  const utcTimestamp = timestamp.endsWith("Z") ? timestamp : `${timestamp}Z`;
  const d = new Date(utcTimestamp);

  return d.toLocaleDateString("en-GB", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

  const formatTime = (timestamp: string) => {
    // Tell JS this timestamp is UTC
    const utcTimestamp = timestamp.endsWith("Z") ? timestamp : `${timestamp}Z`;

    const d = new Date(utcTimestamp);

    return d.toLocaleTimeString("en-GB", {
      timeZone: "Asia/Kolkata",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };
  return (
    <div className="w-full flex justify-center items-center  bg-[#FFF4F8] min-h-screen">
      <div className="w-[90%] bg-white h-[90vh]">
        <div className="flex flex-row p-2">
          {/* This text is hidden on small screens and only shown on large screens */}
          <h2 className="hidden lg:block text-lg text-indira_text font-semibold mb-6 lg:w-[50%] p-4">
            Showing threads of
            <span className="font-bold">
              {" "}
              {month}, {year}
            </span>
          </h2>

          <div className="flex items-center justify-end gap-3 mb-4 p-4 w-full lg:w-[50%]">
            <MonthYearSelect setYear={setYear} setMonth={setMonth} />

            <input
              className="flex justify-end bg-white text-indira_text border border-indira_border px-3 py-2 rounded-md text-sm w-[30%] focus:outline-none"
              placeholder="Search"
              type="text"
              value={thread_id}
              onChange={(e) => setthread_id(e.target.value)}
            />
          </div>
        </div>
        <div className="p-4 h-[calc(90vh-120px)] overflow-y-auto no-scrollbar">
          <div className="overflow-x-auto  rounded-md bg-white shadow-sm">
            <table className="w-full text-sm md:text-base">
              <thead className="bg-gray-100 border border-indira_border text-indira_text">
                <tr>
                  <th className="text-left p-3 font-medium">THREAD</th>
                  <th className="text-left p-3 font-medium">NAME</th>
                  <th className="text-left p-3 font-medium">DATE</th>
                  <th className="text-left p-3 font-medium">TIME</th>
                  <th className="text-left p-3 font-medium">ACTION</th>
                </tr>
              </thead>
              <tbody className="border border-indira_border">
                {data.map((row, i) => (
                  <tr
                    key={i}
                    className=" cursor-pointer border border-indira_hello_border hover:border-indira_border hover:bg-indira_light_red text-indira_text"
                  >
                    <td className="p-3">{row._id}</td>
                    <td className="p-3">{row.thread_name || "N/A"}</td>
                    <td className="p-3">{formatDate(row.timestamp)}</td>
                    <td className="p-3">{formatTime(row.timestamp)}</td>
                    <td
                      className="p-3 text-blue-600 cursor-pointer hover:underline"
                      onClick={() => {
                        setSelectedThread(row); // row contains thread data
                        setBotUI(true);
                      }}
                    >
                      View
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {botui && <BOTUI setBotUI={setBotUI} thread={selectedThread} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
