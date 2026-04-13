"use client";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

type DashboardStats = {
  userId: number;
  data: {
    queue: {
      pending: number;
    };
    stats: {
      fetch_today: number;
      completed: number;
      pending: number;
    };
  };
  button: string;
};

const DashboardPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const gmailStatus = searchParams.get("gmail");
  const [websocket_incoming_data, setStats] = useState<DashboardStats | null>(
    null,
  );
  const [isFetching, setIsFetching] = useState(false);
  useEffect(() => {
    if (gmailStatus === "connected") {
      alert("Gmail connected successfully!");
      // toast.success("Gmail connected successfully!", {
      //   duration: 5000,
      //   position: "top-right",
      // });
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
        console.log("WebSocket connected successfully");
        reconnectAttempts = 0; // reset on successful connection
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received websocket data:", data);
        setStats(data);
        if (data.button === "true") setIsFetching(true);
        else setIsFetching(false);
      };

      ws.onerror = (err) => {
        console.log("WebSocket error -> ", err);
      };

      ws.onclose = (event) => {
        console.log("WebSocket closed, code:", event.code);

        // Don't reconnect if auth failed
        if (event.code === 1008) {
          router.push("/login");
          return;
        }

        // Reconnect with exponential backoff
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(1000 * 2 ** reconnectAttempts, 30000);
          console.log(
            `Reconnecting in ${delay / 1000}s (attempt ${reconnectAttempts + 1})`,
          );
          reconnectTimeout = setTimeout(() => {
            reconnectAttempts++;
            connect();
          }, delay);
        } else {
          console.log("Max reconnect attempts reached");
        }
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      ws.close();
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
            {websocket_incoming_data?.data?.stats?.completed}
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
