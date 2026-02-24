import Image from "next/image";
import Link from "next/link";

async function getMails() {
  const res = await fetch("http://127.0.0.1:8000/get-all-reports", {
    cache: "no-store", // disable caching (optional)
  });

  if (!res.ok) {
    throw new Error("Failed to fetch data");
  }

  return res.json();
}

const DashboardPage = async () => {
  const mails = await getMails();

  return (
    <div>
      <div className="text-black text-3xl pt-12">Emails - Inbox</div>
      <div className="flex gap-4 pt-5 ">
        <div className="text-black text-l pt-4 whitespace-nowrap mb-2">
          Real-time visibility into fetched emails and AI analysis status
        </div>
        <div className="flex items-center border text-black border-gray-300 h-15 rounded-md px-6 mb-2">
          <span className="text-l whitespace-nowrap w-0">
            Next fetch: Today 6:00 PM
          </span>
          <span className="pl-76">
            <Link
              href="/update-dashboard"
              className="bg-blue-600 text-white px-10 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition"
            >
              <div className="flex items-center justify-center">
                <svg
                  className="center"
                  width="20"
                  height="25"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org"
                >
                  <path
                    d="M19 12H5"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M12 19l-7-7 7-7"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            </Link>
          </span>
        </div>
      </div>

      <div className="mb-2">
        <div className="border text-black border-gray-300 h-20 rounded-md">
          <span className="text-2xl pl-4">Emails</span>
          <span className="pl-150">
            <Link
              href="/update-dashboard"
              className="bg-blue-600 text-white px-3 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition mt-3"
            >
              <div className="flex items-center justify-center">
                <svg
                  className="center"
                  width="20"
                  height="25"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M21 12a9 9 0 1 1-2.64-6.36"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M21 3v6h-6"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              Fetch Emails Now
            </Link>
          </span>
        </div>
      </div>
      <table className="border border-gray-300 w-full text-center text-black">
        <thead className="bg-gray-100">
          <tr>
            <th className="border px-4 py-2">Status</th>
            <th className="border px-4 py-2">Subject</th>
            <th className="border px-4 py-2">From</th>
            <th className="border px-4 py-2">Received</th>
            <th className="border px-4 py-2">View</th>
          </tr>
        </thead>
        <tbody>
          {mails.map((mail: any) => (
            <tr className="border-t">
              <td className="border px-4 py-2 text-green-600">{mail.status}</td>
              <td className="border px-4 py-2">{mail.subject}</td>
              <td className="border px-4 py-2">{mail.mail_from}</td>
              <td className="border px-4 py-2">{mail.received_at}</td>
              <th className="border px-4 py-2">
                <a
                  href="/report/1"
                  className="text-blue-600 hover:underline text-center"
                >
                  View Mail
                </a>
              </th>
            </tr>
          ))}
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
