"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Eye,
  Plus,
  CheckCircle,
  Clock,
  Mail,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

type User = {
  email: string;
  profile_photo_url: string;
  username: string;
  schedule: {
    schedule_time: string;
    id: Number;
    next_run_at: string;
    schedule_frequency: string;
    last_run_at: string;
    user_id: Number;
  };
};

async function getMails(page: any, router: any) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-all-reports?page=${page}&limit=5`,
    { cache: "no-store", credentials: "include" },
  );
  if (res.status === 401) router.push("/login");
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}

const StatusBadge = ({ status }: { status: string }) => {
  const s = (status || "").toLowerCase();
  if (s === "completed" || s === "done") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-100">
        <CheckCircle size={10} />
        Completed
      </span>
    );
  }
  if (s === "pending") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-100">
        <Clock size={10} />
        Pending
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
      {status}
    </span>
  );
};

const DashboardPage = () => {
  const router = useRouter();
  const [mails, setMailData] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [userDetail, setUserDetail] = useState<User | null>(null);

  async function handleAddGmail() {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/gmail`,
      { cache: "no-store", credentials: "include" },
    );
    if (res.status === 401) {
      router.push("/login");
      return;
    }
    if (!res.ok) throw new Error("Failed to fetch data");
    const data = await res.json();
    router.push(data);
  }

  useEffect(() => {
    async function fetchData() {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/user-details`,
        { cache: "no-store", credentials: "include" },
      );
      if (res.status === 401) {
        router.push("/login");
        return;
      }
      if (!res.ok) throw new Error("Failed to fetch data");
      const res_data = await res.json();
      setUserDetail(res_data);
      const mails_Data = await getMails(page, router);
      setMailData(mails_Data);
    }
    fetchData();
  }, [page]);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email Inbox</h1>
          <p className="text-sm text-gray-500 mt-1">
            Real-time visibility into fetched emails and AI analysis status
          </p>
        </div>
        <div className="mt-1 flex-shrink-0">
          {userDetail !== null && userDetail.email === null && (
            <button
              onClick={handleAddGmail}
              className="inline-flex items-center gap-2 bg-indigo-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-indigo-700 transition shadow-sm shadow-indigo-200"
            >
              <Plus size={15} />
              Add Gmail Account
            </button>
          )}
          {userDetail !== null && userDetail.email !== null && (
            <div className="inline-flex items-center gap-2 border border-indigo-200 bg-indigo-50 text-indigo-700 text-sm font-medium px-4 py-2.5 rounded-xl">
              <Mail size={14} />
              {userDetail.email}
            </div>
          )}
        </div>
      </div>

      {/* Table card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm table-fixed">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/70">
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide w-32">
                Status
              </th>
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Subject
              </th>
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide w-40">
                From
              </th>
              <th className="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide w-36">
                Received
              </th>
              <th className="text-center px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide w-20">
                View
              </th>
            </tr>
          </thead>
          <tbody>
            {mails.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-16 text-gray-400">
                  <Mail
                    size={36}
                    className="mx-auto mb-3 opacity-20 text-gray-400"
                  />
                  <p className="text-sm font-medium text-gray-400">
                    No emails found
                  </p>
                  <p className="text-xs text-gray-300 mt-1">
                    Connect your Gmail account to start fetching emails
                  </p>
                </td>
              </tr>
            ) : (
              mails.map((mail: any) => (
                <tr
                  key={mail.id}
                  className="border-b border-gray-50 hover:bg-gray-50/60 transition-colors"
                >
                  <td className="px-5 py-4">
                    <StatusBadge status={mail.status} />
                  </td>
                  <td className="px-5 py-4">
                    <p className="font-medium text-gray-900 truncate">
                      {mail.subject}
                    </p>
                  </td>
                  <td className="px-5 py-4 text-gray-500 text-xs truncate">
                    {mail.mail_from}
                  </td>
                  <td className="px-5 py-4 text-gray-400 text-xs whitespace-nowrap">
                    {mail.received_at}
                  </td>
                  <td className="px-5 py-4 text-center">
                    <Link
                      href={`/email-ai-analysis/${mail.imap_uid}`}
                      className="inline-flex items-center justify-center p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      <Eye size={15} />
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
              disabled={mails?.length < 5}
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
