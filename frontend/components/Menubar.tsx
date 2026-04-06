"use client";

import Image from "next/image";
import Link from "next/link";

import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import { useRouter } from "next/navigation";

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

const menuItems = [
  {
    title: "MENUBAR",
    items: [
      {
        icon: "/home-icon.png",
        label: "Home",
        href: "/home",
      },
      {
        icon: "/report-icon.png",
        label: "Reports",
        href: "/reports",
      },
      {
        icon: "/generate-icon.png",
        label: "Email AI Analysis",
        href: "/email-ai-analysis",
      },
      {
        icon: "/schedule-icon.png",
        label: "Schedules",
        href: "/schedules",
      },
    ],
  },
  {
    title: "Dashboard-update-status",
    items: [
      {
        icon: "/settings-icon.png",
        label: "Settings",
        href: "/settings",
      },
    ],
  },
];

const Menubar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [userDetail, setdetail] = useState<User | null>(null);

  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/logout", {
        method: "POST",
        credentials: "include", // important for cookies
      });

      if (!res.ok) {
        alert("Logout failed");
        return;
      }

      // redirect to login page
      router.push("/login");
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchSchedule = async () => {
      const res = await fetch(`http://localhost:8000/user-details`, {
        cache: "no-store",
        credentials: "include",
      });
      console.log("Hello Menubar===>", res);
      if (res.status === 401) {
        window.location.href = "/login";
      }

      if (!res.ok) {
        throw new Error("Failed to fetch data");
      }
      const data = await res.json();
      setdetail({
        email: data.email,
        profile_photo_url: data.profile_photo_url,
        username: data.username,
        schedule: data.schedule,
      });
    };

    fetchSchedule();
  }, []);

  return (
    <div className=" text-sm">
      <div className="md:hidden flex items-center justify-between p-4 border-b">
        <button
          onClick={() => setIsOpen(true)}
          className="text-black p-2 rounded-lg hover:bg-blue-700 transition duration-200"
        >
          <Menu size={24} />
        </button>
      </div>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
      <aside
        className={`
          fixed md:static top-0 left-0 h-screen w-64 bg-white border-r z-50
          transform transition-transform duration-300
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0
        `}
      >
        <div className="md:hidden flex justify-end p-4">
          <button onClick={() => setIsOpen(false)}>
            <X size={24} />
          </button>
        </div>
        <div className="pt-6"></div>
        {menuItems.map((i) => (
          <div className="flex-col pt-2" key={i.title}>
            {i.items.map((item) => {
              return (
                <Link
                  href={item.href}
                  key={item.label}
                  className="flex items-center justify-center gap-4 text-gray-500 py-2 md:px-2 rounded-md hover:bg-lamaSkyLight"
                >
                  <Image src={item.icon} alt="" width={20} height={20} />
                  <span className="lg:block">{item.label}</span>
                </Link>
              );
            })}
          </div>
        ))}
        <div className="pt-10"></div>
        <div className="box text-gray-700">
          <h4>
            <span className="inline-flex gap-1">
              <Image src="/refresh-icon.png" alt="" width={20} height={20} />
              Dashboard Update
            </span>
          </h4>
          <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">
              Schedule Details
            </h2>

            <div className="space-y-2 text-gray-700">
              <p>
                <span className="font-medium">Last Run:</span>{" "}
                {userDetail?.schedule?.last_run_at || "N/A"}
              </p>

              <p>
                <span className="font-medium">Next Run:</span>{" "}
                {userDetail?.schedule?.next_run_at || "N/A"}
              </p>

              <p>
                <span className="font-medium">Frequency:</span>{" "}
                {userDetail?.schedule?.schedule_frequency || "N/A"}
              </p>

              <p>
                <span className="font-medium">Time:</span>{" "}
                {userDetail?.schedule?.schedule_time || "N/A"}
              </p>
            </div>
          </div>
          <div>
            <label className="radio">
              <span className="custom-radio"></span>
            </label>
          </div>
        </div>
        <div className="mt-auto flex items-center gap-2 px-2 text-gray-500 pt-19">
          <img
            src={userDetail?.profile_photo_url}
            className="w-10 h-10 rounded-full"
          />
          <div className="lg:block">
            <strong>{userDetail?.username}</strong>
          </div>
        </div>
        <button
          onClick={handleLogout}
          disabled={loading}
          className="px-2 py-2 bg-red-500 text-white rounded-lg hover:bg-red-400 transition mr-100"
        >
          {loading ? "Logging out..." : "Logout"}
        </button>
      </aside>
    </div>
  );
};

export default Menubar;
