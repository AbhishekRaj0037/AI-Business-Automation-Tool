import Image from "next/image";
import Link from "next/link";

const DashboardPage = () => {
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

            <form className="space-y-6">
              {/* Schedule Time */}
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Schedule Time
                </label>

                <div className="flex gap-3">
                  <select className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {[...Array(12)].map((_, i) => (
                      <option key={i}>{String(i + 1).padStart(2, "0")}</option>
                    ))}
                  </select>

                  <select className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {[...Array(60)].map((_, i) => (
                      <option key={i}>{String(i).padStart(2, "0")}</option>
                    ))}
                  </select>

                  <select className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
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

                <select className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Every day</option>
                  <option>Every 6 hours</option>
                  <option>Every 12 hours</option>
                  <option>Weekly</option>
                </select>
              </div>

              {/* Save Button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Save Schedule
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
