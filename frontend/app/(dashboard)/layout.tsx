import Menubar from "@/components/Menubar";
import { Toaster } from "sonner";

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Menubar />
      <main className="flex-1 overflow-auto">
        <div className="w-full max-w-5xl mx-auto">{children}</div>
        <Toaster richColors position="top-right" />
      </main>
    </div>
  );
}
