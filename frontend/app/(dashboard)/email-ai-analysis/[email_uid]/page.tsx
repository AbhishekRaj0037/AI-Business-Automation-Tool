import Image from "next/image";
import Link from "next/link";

const DashboardPage = () => {
  return (
    <div>
      <div className="mb-2 mt-4">
        <div className="border text-black border-gray-300 h-20 rounded-md pt-6">
          <span className="text-2xl pl-4 mt-4">
            Urgent: Quarterly Report Preparation Needed
          </span>
        </div>
        <div className="border text-black border-gray-300 h-20 rounded-md flex items-center gap-3 px-4">
          <img
            src="https://i.pravatar.cc/40"
            className="w-10 h-10 rounded-full"
            alt="profile"
          />
          <span className="font-semibold m-2">
            <div>Jane Smith {"<jane.smith@example.com>"}</div>
            <div>To: John Doe</div>
          </span>
          <span className="pl-60">Received: Yesterday, 3:24 PM</span>
        </div>
      </div>
      <div className="text-black text-lg border border-black p-4">
        Email Body
      </div>
      <div className="text-black border border-black mb-4">
        <p className="m-4">
          Hi John, I hope you're doing well. Just a reminder that the quarterly
          report is due next Friday. Could you please start preparing the
          necessary documents and ensure that all data from the past three
          months is accurate and up to date? If you need any additional
          resources or assistance, let me know. Thanks so much for handling
          this.{" "}
        </p>
        <p className="m-4">Best, Jane</p>
      </div>
      <table className="border border-gray-300 w-full text-left text-black">
        <thead className="bg-gray-100 text-center">
          <tr>
            <th className="border px-4 py-2 text-center">Attachments</th>
            <th className="border px-4 py-2 text-center">File Type</th>
            <th className="border px-4 py-2 text-center">Size</th>
            <th className="border px-4 py-2 text-center">AI Analysis</th>
            <th className="border px-4 py-2 text-center">View</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-t">
            <td className="border px-4 py-2 text-green-600 text-center">
              Quarterly_Report_Template.pdf
            </td>
            <td className="border px-4 py-2 text-center">PDF</td>
            <td className="border px-4 py-2 text-center">1.2MB</td>
            <td className="border px-4 py-2 text-center">
              <a href="/report/1" className="text-blue-600 hover:underline">
                Give it to AI
              </a>
            </td>
            <td className="border px-4 py-2">
              <div className="flex justify-center items-center h-full">
                <a href="/report/1" className="text-blue-600 hover:underline">
                  <svg
                    width="20"
                    height="25"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <circle
                      cx="12"
                      cy="12"
                      r="3"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </a>
              </div>
            </td>
          </tr>

          <tr className="border-t">
            <td className="border px-4 py-2 text-yellow-600 text-center">
              FINANCIAL_DATA_Q1_2024.xlsx
            </td>
            <td className="border px-4 py-2 text-center">Excel</td>
            <td className="border px-4 py-2 text-center">650KB</td>
            <td className="border px-4 py-2 text-center">
              <a href="/report/1" className="text-blue-600 hover:underline">
                Give it to AI
              </a>
            </td>
            <td className="border px-4 py-2">
              <div className="flex justify-center items-center h-full">
                <a href="/report/1" className="text-blue-600 hover:underline">
                  <svg
                    width="20"
                    height="25"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <circle
                      cx="12"
                      cy="12"
                      r="3"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </a>
              </div>
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
