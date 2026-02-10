import Menubar from "@/components/Menubar";
import Image from "next/image";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="h-screen flex">
      <aside className="w-64 border-r">
        <Menubar />
      </aside>

      <main className="flex-1 flex justify-center overflow-y-auto p-6">
        <div className="w-full max-w-6xl">{children}</div>
      </main>
    </div>
  );
}
