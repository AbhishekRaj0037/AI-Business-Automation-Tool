import Image from "next/image";
import Link from "next/link";

const DashboardPage = () => {
  return (
    <div>
      <div className="text-black text-3xl pt-12 pb-3">Generated Reports</div>
      <div className="mb-2">
        <div className="border text-black border-gray-300 h-20 rounded-md">
          <span className="text-2xl pl-4">Reports</span>

          <span className="pl-120">
            <input
              type="text"
              id="search"
              placeholder="Search reports..."
              className="border border-black rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            />
            <Link
              href="/update-dashboard"
              className="bg-blue-600 text-white px-3 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition mt-3 ml-2"
            >
              <div className="flex items-center justify-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                >
                  <line x1="4" y1="8" x2="20" y2="8" />
                  <line x1="4" y1="16" x2="20" y2="16" />
                </svg>
              </div>
              Filter
            </Link>
          </span>
        </div>
      </div>
      <table className="border border-gray-300 w-full text-left text-black">
        <thead className="bg-gray-100 text-center">
          <tr>
            <th className="border px-4 py-2 text-center">Date & Time</th>
            <th className="border px-4 py-2 text-center">Report Type</th>
            <th className="border px-4 py-2 text-center">Email Processed</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-t">
            <td className="border px-4 py-2 text-green-600 text-center">
              Today 3:45 PM
            </td>
            <td className="border px-4 py-2 text-center">
              Daily Email Summary
            </td>
            <td className="border px-4 py-2 text-center">
              <a href="/report/1" className="text-blue-600 hover:underline">
                View Report
              </a>
            </td>
          </tr>

          <tr className="border-t">
            <td className="border px-4 py-2 text-yellow-600 text-center">
              Today 1:20 PM
            </td>
            <td className="border px-4 py-2 text-center">
              Daily Email Summary
            </td>
            <td className="border px-4 py-2 text-center">
              <a
                href="/report/1"
                className="text-blue-600 hover:underline text-center"
              >
                View Report
              </a>
            </td>
          </tr>
        </tbody>
      </table>
      <div className="flex items-center justify-between px-6 py-4 border-t rounded-b-xl text-black">
        {/* Left side */}
        <span className="text-sm text-gray-600">
          Showing 1 to 10 of 50 entries
        </span>

        {/* Right side Pagination */}
        <div className="flex items-center gap-2">
          <button className="px-3 py-1 border rounded-md text-gray-600 hover:bg-gray-100">
            Previous
          </button>

          <button className="px-3 py-1 bg-blue-600 text-white rounded-md">
            1
          </button>

          <button className="px-3 py-1 border rounded-md hover:bg-gray-100">
            2
          </button>

          <button className="px-3 py-1 border rounded-md hover:bg-gray-100">
            3
          </button>

          <button className="px-3 py-1 border rounded-md text-gray-600 hover:bg-gray-100">
            Next
          </button>
        </div>
      </div>
      <p className="text-black pt-2">
        • Al analysis runs continuously. Most emails are processed within 2-5
        minutes.
      </p>
    </div>
  );
};

export default DashboardPage;
