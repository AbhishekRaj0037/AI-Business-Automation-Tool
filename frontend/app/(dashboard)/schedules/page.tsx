"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Image from "next/image";
import Link from "next/link";

const DashboardPage = () => {
  const router = useRouter();
  const [buttonStatus, setButtonStatus] = useState(false);
  const handleSubmit = async (e: any) => {
    e.preventDefault();

    const data = {
      hour,
      minute,
      period,
      frequency,
    };
    setButtonStatus(true);

    try {
      const [res] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/schedule-jobs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(data),
        }),
        new Promise((resolve) => setTimeout(resolve, 2000)), // minimum 2 sec delay
      ]);
      if (res.status === 401) {
        router.push("/login");
      }

      if (!res.ok) {
        throw new Error("Failed to save schedule");
      }

      const result = await res.json();
      console.log("Saved:", result);
      setButtonStatus(false);
      window.location.reload();
    } catch (err) {
      console.error("Error:", err);
    }
  };
  const [hour, setHour] = useState("01");
  const [minute, setMinute] = useState("00");
  const [period, setPeriod] = useState("AM");
  const [frequency, setFrequency] = useState("everyday");
  return (
    <div>
      <div className="text-black text-3xl pt-12">Schedules</div>
      <div className="flex gap-4 pt-5 ">
        <div className="text-black text-l pt-4 whitespace-nowrap mb-2">
          Set automatic times for dashboard updates
        </div>
      </div>

      <div className="mb-2">
        <div className="border text-black border-gray-300 h-17 rounded-md pt-4 pl-4 text-xl">
          Schedules
        </div>
        <div className="border text-black border-gray-300 h-15 rounded-md pt-4 pl-4 text-l">
          Set automatic times for dashboard updates
        </div>
        <div className="border text-black border-gray-300 h-100 rounded-md pt-4 pl-4 text-xl">
          <div className="w-full max-w-2xl mx-auto mt-10">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
              Schedule Dashboard Updates
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Schedule Time */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Schedule Time
                </label>

                <div className="flex gap-3">
                  <select
                    value={hour}
                    onChange={(e) => setHour(e.target.value)}
                  >
                    {[...Array(12)].map((_, i) => (
                      <option key={i}>{String(i + 1).padStart(2, "0")}</option>
                    ))}
                  </select>

                  <select
                    value={minute}
                    onChange={(e) => setMinute(e.target.value)}
                  >
                    {[...Array(60)].map((_, i) => (
                      <option key={i}>{String(i).padStart(2, "0")}</option>
                    ))}
                  </select>

                  <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                  >
                    <option>AM</option>
                    <option>PM</option>
                  </select>
                </div>

                <p className="text-sm text-gray-500 mt-2">
                  Time is in your local time zone
                </p>
              </div>

              {/* Frequency */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Frequency
                </label>

                <select
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                >
                  <option value="everyday">Every day</option>
                  <option value="every_six_hours">Every 6 hours</option>
                  <option value="every_twelve_hours">Every 12 hours</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              {/* Save Button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  {buttonStatus ? "Scheduling please wait..." : "Save Schedule"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
