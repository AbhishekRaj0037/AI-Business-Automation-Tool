"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  Home,
  FileText,
  Sparkles,
  Mail,
  Clock,
  Settings,
  Menu,
  X,
  RefreshCw,
  LogOut,
  Zap,
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

const navItems = [
  { icon: Home, label: "Home", href: "/home" },
  { icon: FileText, label: "Reports", href: "/reports" },
  { icon: Sparkles, label: "Generate Reports", href: "/generate-report" },
  { icon: Mail, label: "Email AI Analysis", href: "/email-ai-analysis" },
  { icon: Clock, label: "Schedules", href: "/schedules" },
];

const Menubar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [userDetail, setdetail] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/logout`,
        { method: "POST", credentials: "include" }
      );
      if (!res.ok) {
        alert("Logout failed");
        return;
      }
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
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/user-details`,
        { cache: "no-store", credentials: "include" }
      );
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      if (!res.ok) throw new Error("Failed to fetch data");
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

  const NavLink = ({ item }: { item: (typeof navItems)[0] }) => {
    const isActive = pathname === item.href;
    const Icon = item.icon;
    return (
      <Link
        href={item.href}
        onClick={() => setIsOpen(false)}
        className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group ${
          isActive
            ? "bg-indigo-50 text-indigo-700"
            : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
        }`}
      >
        <Icon
          size={17}
          className={
            isActive
              ? "text-indigo-600"
              : "text-gray-400 group-hover:text-gray-600"
          }
        />
        <span className="flex-1">{item.label}</span>
        {isActive && (
          <div className="w-1.5 h-1.5 rounded-full bg-indigo-600 flex-shrink-0" />
        )}
      </Link>
    );
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Brand */}
      <div className="px-4 py-5 border-b border-gray-100 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-200">
            <Zap size={17} className="text-white" />
          </div>
          <div>
            <p className="font-bold text-gray-900 text-sm leading-tight">
              AI Business
            </p>
            <p className="text-xs text-gray-400">Automation Assistant</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2 mb-3">
          Navigation
        </p>
        {navItems.map((item) => (
          <NavLink key={item.href} item={item} />
        ))}

        <div className="pt-5">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2 mb-3">
            Account
          </p>
          {(() => {
            const isActive = pathname === "/settings";
            return (
              <Link
                href="/settings"
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`}
              >
                <Settings
                  size={17}
                  className={
                    isActive
                      ? "text-indigo-600"
                      : "text-gray-400 group-hover:text-gray-600"
                  }
                />
                <span className="flex-1">Settings</span>
                {isActive && (
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-600" />
                )}
              </Link>
            );
          })()}
        </div>
      </nav>

      {/* Schedule Info */}
      <div className="mx-3 mb-3 p-3 bg-gradient-to-br from-indigo-50 to-violet-50 rounded-xl border border-indigo-100 flex-shrink-0">
        <div className="flex items-center gap-2 mb-2.5">
          <RefreshCw size={13} className="text-indigo-600" />
          <span className="text-xs font-semibold text-indigo-700">
            Dashboard Updates
          </span>
        </div>
        <div className="space-y-1.5">
          {[
            { label: "Last run", value: userDetail?.schedule?.last_run_at },
            { label: "Next run", value: userDetail?.schedule?.next_run_at },
            {
              label: "Frequency",
              value: userDetail?.schedule?.schedule_frequency,
            },
            { label: "At", value: userDetail?.schedule?.schedule_time },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between text-xs">
              <span className="text-gray-400">{label}</span>
              <span className="font-medium text-gray-700 truncate ml-2 max-w-[100px]">
                {value || "N/A"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* User profile */}
      <div className="px-3 pb-4 border-t border-gray-100 pt-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="relative flex-shrink-0">
            <img
              src={
                userDetail?.profile_photo_url ||
                "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
              }
              className="w-8 h-8 rounded-full ring-2 ring-indigo-100 object-cover"
              alt="avatar"
            />
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">
              {userDetail?.username || "User"}
            </p>
            <p className="text-xs text-gray-400 truncate">
              {userDetail?.email || "No email"}
            </p>
          </div>
          <button
            onClick={handleLogout}
            disabled={loading}
            title="Logout"
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
          >
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="text-sm">
      {/* Mobile header */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-gray-100 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center">
            <Zap size={13} className="text-white" />
          </div>
          <span className="font-bold text-gray-900 text-sm">AI Business</span>
        </div>
        <button
          onClick={() => setIsOpen(true)}
          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed md:static top-0 left-0 h-screen w-64 bg-white border-r border-gray-100 z-50 shadow-sm
          transform transition-transform duration-300
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0
        `}
      >
        {/* Mobile close btn */}
        <div className="md:hidden flex justify-end p-3 border-b border-gray-100">
          <button
            onClick={() => setIsOpen(false)}
            className="p-1.5 hover:bg-gray-100 rounded-lg"
          >
            <X size={18} />
          </button>
        </div>
        <div className="h-full">
          <SidebarContent />
        </div>
      </aside>
    </div>
  );
};

export default Menubar;
