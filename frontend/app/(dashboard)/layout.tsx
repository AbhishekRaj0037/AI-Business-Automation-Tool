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
      <div className="w-[14%] md:w-[8%] lg:w-[16%] xl:w-[14%] bg-red-200">
        <Menubar />
      </div>

      <div className="w-[86%%] md:w-[92%%] lg:w-[84%%] xl:w-[86%%] bg-red-50"></div>
    </div>
  );
}
