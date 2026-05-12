"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Clock, Save, Loader2, Calendar } from "lucide-react";

const FREQUENCY_OPTIONS = [
  {
    value: "everyday",
    label: "Every Day",
    desc: "Runs once daily at the set time",
  },
  {
    value: "every_six_hours",
    label: "Every 6 Hours",
    desc: "Runs 4 times a day",
  },
  {
    value: "every_twelve_hours",
    label: "Every 12 Hours",
    desc: "Runs twice a day",
  },
  { value: "weekly", label: "Weekly", desc: "Runs once a week" },
];

const DashboardPage = () => {
  const router = useRouter();
  const [buttonStatus, setButtonStatus] = useState(false);
  const [hour, setHour] = useState("01");
  const [minute, setMinute] = useState("00");
  const [period, setPeriod] = useState("AM");
  const [frequency, setFrequency] = useState("everyday");

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    const data = { hour, minute, period, frequency };
    setButtonStatus(true);
    try {
      const [res] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/schedule-jobs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(data),
        }),
        new Promise((resolve) => setTimeout(resolve, 2000)),
      ]);
      if ((res as Response).status === 401) {
        router.push("/login");
        return;
      }
      if (!(res as Response).ok) throw new Error("Failed to save schedule");
      setButtonStatus(false);
      window.location.reload();
    } catch (err) {
      console.error("Error:", err);
      setButtonStatus(false);
    }
  };

  const selectClass =
    "border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent cursor-pointer min-w-[76px] shadow-sm";

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-sm shadow-amber-200">
            <Calendar size={17} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Schedules</h1>
        </div>
        <p className="text-sm text-gray-500 mt-2 ml-12">
          Set automatic times for dashboard updates
        </p>
      </div>

      {/* Form card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <form onSubmit={handleSubmit} className="space-y-7">
          {/* Schedule Time */}
          <div>
            <label className="flex items-center gap-1.5 text-sm font-semibold text-gray-700 mb-3">
              <Clock size={14} className="text-gray-400" />
              Schedule Time
            </label>
            <div className="flex items-center gap-2">
              <select
                value={hour}
                onChange={(e) => setHour(e.target.value)}
                className={selectClass}
              >
                {[...Array(12)].map((_, i) => (
                  <option key={i}>{String(i + 1).padStart(2, "0")}</option>
                ))}
              </select>
              <span className="text-gray-300 font-bold text-xl select-none">
                :
              </span>
              <select
                value={minute}
                onChange={(e) => setMinute(e.target.value)}
                className={selectClass}
              >
                {[...Array(60)].map((_, i) => (
                  <option key={i}>{String(i).padStart(2, "0")}</option>
                ))}
              </select>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className={selectClass}
              >
                <option>AM</option>
                <option>PM</option>
              </select>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Time is in your local time zone
            </p>
          </div>

          {/* Frequency */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Frequency
            </label>
            <div className="grid grid-cols-2 gap-3">
              {FREQUENCY_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setFrequency(opt.value)}
                  className={`text-left px-4 py-3 rounded-xl border transition-all duration-150 ${
                    frequency === opt.value
                      ? "border-indigo-300 bg-indigo-50 text-indigo-700 shadow-sm"
                      : "border-gray-200 text-gray-600 hover:border-indigo-200 hover:bg-gray-50"
                  }`}
                >
                  <p className="text-sm font-semibold">{opt.label}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{opt.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-1">
            <button
              type="submit"
              disabled={buttonStatus}
              className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition shadow-sm shadow-indigo-200 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {buttonStatus ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Saving…
                </>
              ) : (
                <>
                  <Save size={14} />
                  Save Schedule
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DashboardPage;
