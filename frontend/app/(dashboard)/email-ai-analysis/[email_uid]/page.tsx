"use client";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

async function getMail(imap_uid: any) {
  const res = await fetch(
    `http://127.0.0.1:8000/get-reports-by-id?imap_uid=${imap_uid}`,
    {
      cache: "no-store", // disable caching (optional)
    },
  );

  if (!res.ok) {
    throw new Error("Failed to fetch data");
  }
  const data = await res.json();
  return data;
}

const DashboardPage = () => {
  const router = useRouter();
  const [email, setEmailData] = useState<any>(null);
  const params = useParams();
  useEffect(() => {
    async function fetchData() {
      const res = await fetch("http://localhost:8000/me", {
        method: "GET",
        credentials: "include",
      });
      const result = await res.json();
      if (!res.ok) {
        router.push("/login");
        return;
      }
      // setEmail(result);
      const mail_Data = await getMail(params.email_uid);
      setEmailData(mail_Data);
    }
    fetchData();
  }, []);
  return (
    <>
      {email && (
        <div>
          <div className="mb-2 mt-4 text-black">
            <div className="border text-black border-gray-300 h-20 rounded-md pt-6">
              <span className="text-2xl pl-4 mt-4">{email.subject}</span>
            </div>
            <div className="border text-black border-gray-300 h-20 rounded-md flex items-center gap-3 px-4">
              <img
                src="https://i.pravatar.cc/40"
                className="w-10 h-10 rounded-full"
                alt="profile"
              />
              <span className="font-semibold m-2">
                <div>{email.mail_from}</div>
              </span>
              <span className="pl-60">Received: {email.received_at}</span>
            </div>
          </div>
          <div className="text-black text-lg border border-black p-4">
            Email Body
          </div>
          <div className="text-black border border-black mb-4">
            <p className="m-4">{email.subject}</p>
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
                    <a
                      href="/report/1"
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
                    <a
                      href="/report/1"
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
                </td>
              </tr>
            </tbody>
          </table>

          <p className="text-black pt-2">
            • Al analysis runs continuously. Most emails are processed within
            2-5 minutes.
          </p>
        </div>
      )}
    </>
  );
};

export default DashboardPage;
