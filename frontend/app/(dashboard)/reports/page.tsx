"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Search,
  SlidersHorizontal,
  FileText,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

async function getReports(page: any, router: any) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-all-ai-reports?page=${page}&limit=5`,
    { cache: "no-store", credentials: "include" }
  );
  if (res.status === 401) router.push("/login");
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}

const DashboardPage = () => {
  const router = useRouter();
  const [reports, setReportData] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function fetchData() {
      const data = await getReports(page, router);
      setReportData(data);
    }
    fetchData();
  }, [page]);

  const filtered = search
    ? reports.filter((r) =>
        r.report_name?.toLowerCase().includes(search.toLowerCase())
      )
    : reports;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Generated Reports</h1>
        <p className="text-sm text-gray-500 mt-1">
          Browse and edit your AI-generated reports
        </p>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-5">
        <div className="relative flex-1 max-w-xs">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search reports…"
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          />
        </div>
        <button className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 bg-white transition-colors">
          <SlidersHorizontal size={14} />
          Filter
        </button>
      </div>

      {/* Table card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/70">
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Date & Time
              </th>
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Report Name
              </th>
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Type
              </th>
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Updated At
              </th>
              <th className="text-center px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Action
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-16 text-gray-400">
                  <FileText
                    size={36}
                    className="mx-auto mb-3 opacity-20 text-gray-400"
                  />
                  <p className="text-sm font-medium text-gray-400">
                    No reports found
                  </p>
                  <p className="text-xs text-gray-300 mt-1">
                    Generate your first report to see it here
                  </p>
                </td>
              </tr>
            ) : (
              filtered.map((report: any) => (
                <tr
                  key={report.id}
                  className="border-b border-gray-50 hover:bg-gray-50/60 transition-colors"
                >
                  <td className="px-5 py-4 text-gray-400 text-xs whitespace-nowrap">
                    {report.generated_at}
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <FileText
                        size={14}
                        className="text-indigo-400 flex-shrink-0"
                      />
                      <span className="font-medium text-gray-900">
                        {report.report_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                      {report.report_type}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-gray-400 text-xs whitespace-nowrap">
                    {report.updated_at}
                  </td>
                  <td className="px-5 py-4 text-center">
                    <Link
                      href={`/reports/${report.id}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
                    >
                      <ExternalLink size={11} />
                      Edit
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-5 py-4 border-t border-gray-100">
          <p className="text-xs text-gray-400">Page {page}</p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => p - 1)}
              disabled={page === 1}
              className="p-2 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={15} />
            </button>
            <span className="px-3 py-1 text-sm font-semibold text-gray-700 bg-gray-50 rounded-lg border border-gray-200">
              {page}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={filtered.length < 5}
              className="p-2 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={15} />
            </button>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-400 mt-4 flex items-center gap-1.5">
        <span className="inline-block w-1 h-1 rounded-full bg-gray-300 flex-shrink-0" />
        AI analysis runs continuously. Most emails are processed within 2–5
        minutes.
      </p>
    </div>
  );
};

export default DashboardPage;
