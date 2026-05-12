"use client";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Mail, Brain, Clock, RefreshCw, Play, Square } from "lucide-react";

type DashboardStats = {
  userId: number;
  data: {
    queue: { pending: number };
    stats: { fetch_today: number; completed: number; pending: number };
  };
  button: string;
};

const StatCard = ({
  icon: Icon,
  label,
  value,
  sublabel,
  gradient,
  bgLight,
}: {
  icon: any;
  label: string;
  value: number | undefined;
  sublabel?: string;
  gradient: string;
  bgLight: string;
}) => (
  <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex-1 min-w-[180px]">
    <div
      className={`w-11 h-11 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-4 shadow-sm`}
    >
      <Icon size={21} className="text-white" />
    </div>
    <p className="text-3xl font-bold text-gray-900 tabular-nums">
      {value ?? <span className="text-gray-300">—</span>}
    </p>
    <p className="text-sm font-medium text-gray-700 mt-1">{label}</p>
    {sublabel && <p className="text-xs text-gray-400 mt-0.5">{sublabel}</p>}
  </div>
);

const DashboardPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const gmailStatus = searchParams.get("gmail");
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isFetching, setIsFetching] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    if (gmailStatus === "connected") {
      toast.success("Gmail connected successfully!", {
        duration: 5000,
        position: "top-right",
      });
    }
  }, [gmailStatus]);

  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;

    const connect = () => {
      ws = new WebSocket(`ws://localhost:8000/ws/dashboard`);

      ws.onopen = () => {
        reconnectAttempts = 0;
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setStats(data);
        setIsFetching(data.button === "true");
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      ws.onclose = (event) => {
        setWsConnected(false);
        if (event.code === 1008) {
          router.push("/login");
          return;
        }
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(1000 * 2 ** reconnectAttempts, 30000);
          reconnectTimeout = setTimeout(() => {
            reconnectAttempts++;
            connect();
          }, delay);
        }
      };
    };

    connect();
    return () => {
      clearTimeout(reconnectTimeout);
      ws?.close();
    };
  }, []);

  const handleToggle = async () => {
    if (!isFetching) {
      setIsFetching(true);
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}`, {
        cache: "no-store",
        credentials: "include",
      });
    } else {
      setIsFetching(false);
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/stop-fetching`, {
        cache: "no-store",
        credentials: "include",
      });
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-baseline gap-2 mb-1">
          <h1 className="text-2xl font-bold text-gray-900">
            Email Intelligence
          </h1>
          <span className="text-sm text-gray-400 font-normal">— Today</span>
        </div>
        <p className="text-sm text-gray-500">
          Real-time visibility into inbox activity and AI workload
        </p>
        <div className="flex items-center gap-1.5 mt-2">
          {wsConnected ? (
            <>
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-green-600 font-medium">Live</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 rounded-full bg-gray-300" />
              <span className="text-xs text-gray-400">Connecting…</span>
            </>
          )}
        </div>
      </div>

      {/* Stat cards */}
      <div className="flex gap-4 mb-6 flex-wrap">
        <StatCard
          icon={Mail}
          label="Emails Fetched Today"
          value={stats?.data?.stats?.fetch_today}
          gradient="from-blue-500 to-cyan-400"
          bgLight="bg-blue-50"
        />
        <StatCard
          icon={Brain}
          label="AI Analysis Done"
          value={stats?.data?.stats?.completed}
          gradient="from-violet-500 to-purple-400"
          bgLight="bg-violet-50"
        />
        <StatCard
          icon={Clock}
          label="Pending Analysis"
          value={stats?.data?.queue?.pending}
          sublabel="In Queue"
          gradient="from-amber-500 to-orange-400"
          bgLight="bg-amber-50"
        />
      </div>

      {/* Fetch control card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-gray-900">
              Data Fetch Control
            </h2>
            <p className="text-sm text-gray-400 mt-0.5">
              Trigger or stop live email fetching
            </p>
          </div>
          <button
            onClick={handleToggle}
            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
              isFetching
                ? "bg-red-50 text-red-600 border border-red-200 hover:bg-red-100"
                : "bg-indigo-600 text-white shadow-sm shadow-indigo-200 hover:bg-indigo-700"
            }`}
          >
            {isFetching ? (
              <>
                <Square size={14} />
                Stop Fetching
              </>
            ) : (
              <>
                <Play size={14} />
                Fetch Now
              </>
            )}
          </button>
        </div>

        {isFetching && (
          <div className="mt-4 flex items-center gap-2.5 text-sm text-indigo-700 bg-indigo-50 rounded-xl px-4 py-3">
            <RefreshCw size={14} className="animate-spin flex-shrink-0" />
            <span>
              Fetching emails and running AI analysis in the background…
            </span>
          </div>
        )}
      </div>

      {/* Footer note */}
      <p className="text-xs text-gray-400 flex items-center gap-1.5">
        <span className="inline-block w-1 h-1 rounded-full bg-gray-300 flex-shrink-0" />
        AI analysis runs continuously. Most emails are processed within 2–5
        minutes.
      </p>
    </div>
  );
};

export default DashboardPage;
