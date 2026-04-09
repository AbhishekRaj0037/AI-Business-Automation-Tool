"use client";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

async function getMails(page: any, router: any) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-all-reports?page=${page}&limit=5`,
    {
      cache: "no-store",
      credentials: "include",
    },
  );
  if (res.status === 401) {
    router.push("/login");
  }

  if (!res.ok) {
    throw new Error("Failed to fetch data");
  }
  const data = await res.json();
  return data;
}

const DashboardPage = () => {
  const router = useRouter();
  const [data, setData] = useState(null);
  const [mails, setMailData] = useState<any[]>([]);
  const [emails, setEmails] = useState([]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    async function fetchData() {
      const mails_Data = await getMails(page, router);
      setMailData(mails_Data);
    }
    fetchData();
  }, [page]);

  return (
    <div>
      <div className="text-black text-3xl pt-12">Emails - Inbox</div>

      <div className="text-black text-l pt-4 whitespace-nowrap mb-2">
        Real-time visibility into fetched emails and AI analysis status
      </div>

      <table className="table-fixed break-words border border-gray-300 w-full text-center text-black">
        <thead className="bg-gray-100">
          <tr>
            <th className="border px-4 py-2 w-30">Status</th>
            <th className="border px-4 py-2 w-70">Subject</th>
            <th className="border px-4 py-2">From</th>
            <th className="border px-4 py-2">Received</th>
            <th className="border px-4 py-2 w-20">View</th>
          </tr>
        </thead>
        <tbody>
          {mails.map((mail: any) => (
            <tr className="border-t" key={mail.id}>
              <td className="border px-4 py-2 text-green-600">{mail.status}</td>
              <td className="border px-4 py-2">{mail.subject}</td>
              <td className="border px-4 py-2">{mail.mail_from}</td>
              <td className="border px-4 py-2">{mail.received_at}</td>
              <th className="border px-4 py-2">
                <div className="flex justify-center items-center h-full">
                  <a
                    href={`/email-ai-analysis/${mail.imap_uid}`}
                    className="text-blue-600 hover:underline"
                  >
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
              </th>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex items-center justify-between px-6 py-4 border-t rounded-b-xl text-black">
        {/* Left side */}
        <span className="text-sm text-gray-600"></span>

        {/* Right side Pagination */}
        <div className="flex items-center gap-2">
          <button
            className="px-3 py-1 border rounded-md text-gray-600 hover:bg-gray-100 "
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
          >
            Previous
          </button>

          <button
            className="px-3 py-1 border rounded-md text-gray-600 hover:bg-gray-100"
            onClick={() => setPage(page + 1)}
          >
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
