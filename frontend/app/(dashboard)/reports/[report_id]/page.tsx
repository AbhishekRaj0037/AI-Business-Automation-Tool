"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import TiptapEditor from "@/components/TiptapEditor";
import { useRouter } from "next/navigation";

export default function ReportEditorPage() {
  const router = useRouter();
  const params = useParams();
  const reportId = params.report_id;

  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-report/${reportId}`,
          { credentials: "include" },
        );
        if (res.status === 401) {
          router.push("/login");
          return;
        }
        if (!res.ok) throw new Error("Failed to fetch report");
        const data = await res.json();
        setReport(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [reportId]);

  const handleSave = async (tiptapJson: any) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/update-report/${reportId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ tiptap_json: tiptapJson }),
        },
      );
      if (!res.ok) throw new Error("Failed to save");
      const data = await res.json();
      console.log("Saved version:", data.version);
    } catch (err) {
      console.error("Save error:", err);
    }
  };

  if (loading) return <div className="text-black pt-12">Loading report...</div>;
  if (error) return <div className="text-red-600 pt-12">Error: {error}</div>;
  if (!report) return <div className="text-black pt-12">Report not found</div>;

  return (
    <div className="pt-12 pb-8">
      <h1 className="text-black text-2xl mb-4">{report.title}</h1>
      <p className="text-gray-500 text-sm mb-6">{report.report_summary}</p>
      <TiptapEditor
        content={report.tiptap_json}
        onSave={handleSave}
        reportId={Number(reportId)}
        sourceMap={report.source_map}
      />
    </div>
  );
}
