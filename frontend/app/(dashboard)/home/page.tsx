"use client";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type DashboardStats = {
  username: string;
  data: {
    queue: {
      pending: number;
      processing: number;
      completed: number;
      failed: number;
    };
    stats: {
      fetch_today: number;
      ai_processed_today: number;
    };
  };
};

const DashboardPage = () => {
  const router = useRouter();
  const [websocket_incoming_data, setStats] = useState<DashboardStats | null>(
    null,
  );
  const [data, setData] = useState(null);
  const [isFetching, setIsFetching] = useState(false);
  const handleToggle = async () => {
    if (!isFetching) {
      setIsFetching(true);
      await fetch("http://localhost:8000/", {
        cache: "no-store",
        credentials: "include",
      });
    } else {
      setIsFetching(false);
      await fetch("http://localhost:8000/stop-fetching", {
        cache: "no-store",
        credentials: "include",
      });
    }
  };
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/dashboard`);
    ws.onopen = () => {
      console.log("WebSocket connected successfully");
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Received websocket data:", data);

      setStats(data);
    };
    ws.onerror = (err) => {
      console.log("WebSocket error", err);
    };
    ws.onclose = (event) => {
      console.log("WebSocket closed");
      console.log("Code:", event);
      if (event.code === 1008) {
        window.location.href = "/login";
      }
    };
    return () => ws.close();
  }, []);
  return (
    <div>
      <div className="text-black text-3xl pl-12 pt-12">
        Email Intelligence -Today
      </div>
      <div className="text-black text-l pl-12 pt-4">
        Real-time visibility into inbox activity and AI workload
      </div>
      <div className="flex pl-12 gap-4 pt-5 mb-2">
        <div className="rounded-md bg-blue-100 p-4 text-black w-64 h-35">
          <Image src="/email.png" alt="" width={40} height={40} />
          <div>Email Fetched Today</div>
          <div className="text-3xl">
            {websocket_incoming_data?.data?.stats?.fetch_today}
          </div>
        </div>
        <div className="rounded-md bg-blue-100  p-4 text-black w-64 h-35">
          <Image
            src="/artificial-intelligence.png"
            alt=""
            width={40}
            height={40}
          />
          <div>AI Analysis Done Today</div>
          <div className="text-3xl">
            {websocket_incoming_data?.data?.queue?.completed}
          </div>
        </div>
        <div className="rounded-md bg-blue-100  p-4 text-black w-64 h-35">
          <Image src="/sand-clock.png" alt="" width={40} height={40} />
          <div>Pending Analysis</div>
          <div className="text-3xl">
            {websocket_incoming_data?.data?.queue?.pending}
          </div>
          <div>In Queue</div>
        </div>
      </div>
      <div className="pl-12 mb-2">
        <div className="border text-black border-gray-300 h-20 rounded-md mr-12">
          <span className="text-2xl pl-2">Recent Reports</span>
          <span className="pl-100">
            <button
              onClick={handleToggle}
              className="bg-blue-600 text-white px-3 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition mt-3"
            >
              {isFetching ? "Stop Fetching" : "Fetch Dashboard Now"}
            </button>
          </span>
        </div>
      </div>
      <div className="flex text-black pl-12 gap-5">
        <div className="border w-97 rounded-md">
          <div className="text-gray-500 border text-center">Recent Reports</div>
          <div className="text-sm text-gray-500">Today 1:00 PM</div>
          <div>Daily Email Summary</div>
          <div className="text-gray-500">
            Fetched 356 emails, analysed 267 by AI
          </div>
        </div>
        <div className="border w-97 rounded-md">
          <div className="text-gray-500 border text-center">
            Upcoming Schedule
          </div>
          <div className="text-sm text-gray-500">Today 06:00 PM</div>
          <div>Generate daily email summary</div>
          <div className="text-gray-500">
            Fetched 356 emails, analysed 267 by AI
          </div>
        </div>
      </div>
      <p className="text-black pl-12 pt-2">
        • Al analysis runs continuously. Most emails are processed within 2-5
        minutes.
      </p>
    </div>
  );
};

export default DashboardPage;
