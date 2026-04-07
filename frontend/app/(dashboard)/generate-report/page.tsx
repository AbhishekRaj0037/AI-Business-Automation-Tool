"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

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
      const res = await fetch("http://localhost:8000/query-document", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ query }),
      });

      if (res.status === 401) {
        window.location.href = "/login";
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
    <div>
      <div className="text-black text-3xl pt-12">Generate AI Report</div>

      <div className="text-black text-l pt-4 whitespace-nowrap mb-2">
        Describe what report you want and AI will generate it from your analysed
        documents
      </div>

      <div className="mb-4">
        <div className="border text-black border-gray-300 rounded-md p-4">
          <span className="text-2xl">New Report</span>
        </div>
      </div>

      {/* Prompt input */}
      <div className="border border-gray-300 rounded-md p-6 mb-4">
        <label className="text-black font-semibold text-lg block mb-3">
          What report do you want to generate?
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Generate a detailed analysis of all food orders with total spending, item breakdown, and a summary table..."
          className="w-full h-40 border border-gray-300 rounded-lg p-4 text-black focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />

        {/* Example prompts */}
        <div className="mt-3">
          <span className="text-gray-500 text-sm">Try these:</span>
          <div className="flex flex-wrap gap-2 mt-2">
            {[
              "Analyse all orders and create a spending report",
              "Generate a summary of all policy documents",
              "Create a comparison report of all uploaded files",
            ].map((example) => (
              <button
                key={example}
                onClick={() => setQuery(example)}
                className="text-sm px-3 py-1 border border-gray-300 rounded-full text-gray-600 hover:bg-gray-100"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="border border-red-300 bg-red-50 text-red-600 rounded-md p-4 mb-4">
          {error}
        </div>
      )}

      {/* Generate button */}
      <div className="flex items-center gap-4 mb-4">
        <button
          onClick={handleGenerate}
          disabled={loading || !query.trim()}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <svg
                className="animate-spin h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Generating... (this may take 15-30 seconds)
            </>
          ) : (
            <>
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
              >
                <path d="M12 3v18M3 12h18" />
              </svg>
              Generate Report
            </>
          )}
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="border border-gray-300 rounded-md p-6 mb-4">
          <div className="flex items-center gap-3 text-black">
            <svg
              className="animate-spin h-5 w-5 text-blue-600"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <div>
              <p className="font-semibold">AI is generating your report...</p>
              <p className="text-gray-500 text-sm mt-1">
                Retrieving relevant documents from vector DB, analysing content,
                and structuring the report with source attribution.
              </p>
            </div>
          </div>
        </div>
      )}

      <p className="text-black pt-4">
        • Make sure you have analysed documents first using the AI Analysis
        page. The report is generated from those analysed documents only.
      </p>
      <p className="text-black pt-2">
        • After generation, you can edit the report in real-time and export it
        as PDF or DOCX.
      </p>
    </div>
  );
};

export default GenerateReportPage;
