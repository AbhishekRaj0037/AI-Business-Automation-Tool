"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Loader2, AlertCircle, Lightbulb } from "lucide-react";

const EXAMPLE_PROMPTS = [
  "Analyse all orders and create a spending report",
  "Generate a summary of all policy documents",
  "Create a comparison report of all uploaded files",
];

const GenerateReportPage = () => {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/query-document`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ query }),
        }
      );
      if (res.status === 401) {
        router.push("/login");
        return;
      }
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to generate report");
      }
      const data = await res.json();
      router.push(`/reports/${data.report_id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shadow-violet-200">
            <Sparkles size={17} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Generate AI Report
          </h1>
        </div>
        <p className="text-sm text-gray-500 mt-2 ml-12">
          Describe what report you want and AI will generate it from your
          analysed documents
        </p>
      </div>

      {/* Prompt input card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          What report do you want to generate?
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Generate a detailed analysis of all food orders with total spending, item breakdown, and a summary table…"
          className="w-full h-36 text-sm border border-gray-200 rounded-xl px-4 py-3 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none bg-gray-50/50 transition-colors"
          disabled={loading}
        />

        {/* Example prompts */}
        <div className="mt-4">
          <div className="flex items-center gap-1.5 mb-2.5">
            <Lightbulb size={13} className="text-amber-500" />
            <span className="text-xs font-medium text-gray-500">
              Try these examples:
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_PROMPTS.map((example) => (
              <button
                key={example}
                onClick={() => setQuery(example)}
                disabled={loading}
                className={`text-xs px-3 py-1.5 border rounded-full transition-all duration-150 ${
                  query === example
                    ? "border-indigo-400 bg-indigo-50 text-indigo-700"
                    : "border-gray-200 text-gray-500 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-600"
                }`}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-3 border border-red-200 bg-red-50 text-red-700 rounded-xl px-4 py-3.5 mb-4 text-sm">
          <AlertCircle size={15} className="flex-shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={loading || !query.trim()}
        className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-6 py-3 rounded-xl text-sm font-semibold shadow-md shadow-indigo-200 hover:shadow-lg hover:shadow-indigo-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none mb-4"
      >
        {loading ? (
          <>
            <Loader2 size={15} className="animate-spin" />
            Generating… (15–30 sec)
          </>
        ) : (
          <>
            <Sparkles size={15} />
            Generate Report
          </>
        )}
      </button>

      {/* Loading state */}
      {loading && (
        <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-5 mb-4">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center flex-shrink-0 shadow-sm">
              <Loader2 size={17} className="animate-spin text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-indigo-900">
                AI is generating your report…
              </p>
              <p className="text-xs text-indigo-600/80 mt-1 leading-relaxed">
                Retrieving relevant documents from vector DB, analysing content,
                and structuring the report with source attribution.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Notes */}
      <div className="space-y-1.5 mt-2">
        <p className="text-xs text-gray-400 flex items-center gap-1.5">
          <span className="inline-block w-1 h-1 rounded-full bg-gray-300 flex-shrink-0" />
          Make sure you have analysed documents first using the AI Analysis
          page.
        </p>
        <p className="text-xs text-gray-400 flex items-center gap-1.5">
          <span className="inline-block w-1 h-1 rounded-full bg-gray-300 flex-shrink-0" />
          After generation, you can edit the report in real-time and export it
          as PDF.
        </p>
      </div>
    </div>
  );
};

export default GenerateReportPage;
