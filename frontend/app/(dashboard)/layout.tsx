import Menubar from "@/components/Menubar";
import Image from "next/image";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex min-h-screen">
      <Menubar />
      <main className="flex-1 flex justify-center item-center">
        <div className="w-full max-w-4xl">{children}</div>
      </main>
    </div>
  );
}
