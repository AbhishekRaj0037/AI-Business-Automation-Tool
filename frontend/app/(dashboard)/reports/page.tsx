"use client";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

async function getReports(page: any) {
  const res = await fetch(
    `http://localhost:8000/get-all-ai-reports?page=${page}&limit=5`,
    {
      cache: "no-store",
      credentials: "include",
    },
  );
  if (res.status === 401) {
    window.location.href = "/login";
  }

  if (!res.ok) {
    throw new Error("Failed to fetch data");
  }
  const data = await res.json();
  return data;
}

const DashboardPage = () => {
  const [reports, setReportData] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [selectedFile, setSelectedFile] = useState(null);
  const handleViewFile = async (reportId: any) => {
    try {
      const response = await fetch(
        `/get-ai-reports-by-id?report_id=${reportId}`,
      );
      const data = await response.json();
      setSelectedFile(data.url);
    } catch (error) {
      console.error("Failed to fetch signed URL:", error);
    }
  };
  useEffect(() => {
    async function fetchData() {
      const mails_Data = await getReports(page);
      setReportData(mails_Data);
    }
    fetchData();
  }, [page]);

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
            <th className="border px-4 py-2 text-center">Report Name</th>
            <th className="border px-4 py-2 text-center">Report Type</th>
            <th className="border px-4 py-2 text-center">Updated At</th>
            <th className="border px-4 py-2 text-center">Edit Report</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report: any) => (
            <tr className="border-t" key={report.id}>
              <td className="border px-4 py-2 text-green-600">
                {report.generated_at}
              </td>
              <td className="border px-4 py-2">{report.report_name}</td>
              <td className="border px-4 py-2">{report.report_type}</td>
              <td className="border px-4 py-2">{report.updated_at}</td>
              <td className="border px-4 py-2">
                <div className="flex justify-center items-center h-full">
                  <Link
                    href={`/reports/${report.id}`}
                    className="text-blue-600 hover:underline"
                  >
                    Edit
                  </Link>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
          {/* Close button */}
          <button
            onClick={() => setSelectedFile(null)}
            className="absolute top-5 right-5 text-white text-2xl"
          >
            ✖
          </button>

          {/* File Viewer */}
          <div className="bg-white w-[80%] h-[80%] rounded-lg overflow-hidden shadow-lg">
            {/* PDF / general viewer */}
            <iframe src={selectedFile} className="w-full h-full" />
          </div>
        </div>
      )}
      <div className="flex items-center justify-between px-6 py-4 border-t rounded-b-xl text-black">
        {/* Left side */}

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
