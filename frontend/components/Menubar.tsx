import Image from "next/image";
import Link from "next/link";

const menuItems = [
  {
    title: "MENUBAR",
    items: [
      {
        icon: "/home-icon.png",
        label: "Home",
        href: "/",
      },
      {
        icon: "/report-icon.png",
        label: "Reports",
        href: "/reports",
      },
      {
        icon: "/email-icon.png",
        label: "Emails",
        href: "/emails",
      },
      {
        icon: "/generate-icon.png",
        label: "AI Analysis",
        href: "/ai-analysis",
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
  return (
    <div className="mt-4 text-sm">
      {menuItems.map((i) => (
        <div className="flex flex-col gap-2" key={i.title}>
          {i.items.map((item) => {
            return (
              <Link
                href={item.href}
                key={item.label}
                className="flex items-center justify-center lg:justify-start gap-4 text-gray-500 py-2 md:px-2 rounded-md hover:bg-lamaSkyLight"
              >
                <Image src={item.icon} alt="" width={20} height={20} />
                <span className="hidden lg:block">{item.label}</span>
              </Link>
            );
          })}
        </div>
      ))}
      <div className="hidden lg:block box text-gray-700">
        <h4>
          <span className="inline-flex gap-1">
            <Image src="/refresh-icon.png" alt="" width={20} height={20} />
            Dashboard Update
          </span>
        </h4>
        <div>
          <label className="radio">
            <input type="radio" name="update" checked />
            <span className="custom-radio"></span>
            Today – 6:00 PM
          </label>
        </div>
        <div>
          <label className="radio">
            <input type="radio" name="update" />
            <span className="custom-radio"></span>
            Every 6 hours
          </label>
        </div>
        <div className="pt-2 text-blue-400">
          <Link href="/change-schedule">Change schedule</Link>
        </div>
      </div>
      <div className="mt-auto flex items-center gap-2 px-2 text-gray-500">
        <img
          src="https://i.pravatar.cc/40"
          className="w-10 h-10 rounded-full"
        />
        <div className="hidden lg:block">
          <strong>John Doe</strong>
          <p className="text-xs">john.doe@example.com</p>
        </div>
      </div>
    </div>
  );
};

export default Menubar;
