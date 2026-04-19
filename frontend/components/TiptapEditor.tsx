"use client";
import { useEditor, EditorContent } from "@tiptap/react";
import { generateHTML } from "@tiptap/html";
import StarterKit from "@tiptap/starter-kit";
import { Table } from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableHeader from "@tiptap/extension-table-header";
import TableCell from "@tiptap/extension-table-cell";
import ImageExtension from "@tiptap/extension-image";
import Underline from "@tiptap/extension-underline";
import Placeholder from "@tiptap/extension-placeholder";
import { useState, useRef } from "react";
import Heading from "@tiptap/extension-heading";
import Paragraph from "@tiptap/extension-paragraph";

function ToolbarButton({
  onClick,
  isActive = false,
  children,
}: {
  onClick: () => void;
  isActive?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-2 py-1 rounded text-sm ${
        isActive
          ? "bg-blue-600 text-white"
          : "bg-gray-100 text-black hover:bg-gray-200"
      }`}
    >
      {children}
    </button>
  );
}

const CustomParagraph = Paragraph.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      sources: {
        default: [],
        parseHTML: (element) => {
          const raw = element.getAttribute("data-sources");
          return raw ? JSON.parse(raw) : [];
        },
        renderHTML: (attributes) => {
          if (!attributes.sources?.length) return {};
          return { "data-sources": JSON.stringify(attributes.sources) };
        },
      },
    };
  },
});

const CustomHeading = Heading.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      sources: {
        default: [],
        parseHTML: (element) => {
          const raw = element.getAttribute("data-sources");
          return raw ? JSON.parse(raw) : [];
        },
        renderHTML: (attributes) => {
          if (!attributes.sources?.length) return {};
          return { "data-sources": JSON.stringify(attributes.sources) };
        },
      },
    };
  },
});

const editorExtensions = [
  StarterKit.configure({
    heading: false,
    paragraph: false,
  }),
  CustomParagraph,
  CustomHeading,
  Underline,
  Table.configure({ resizable: true }),
  TableRow,
  TableHeader,
  TableCell,
  ImageExtension.configure({ inline: false }),
  Placeholder.configure({ placeholder: "Start writing your report..." }),
];

const PDF_STYLES = `
  @page {
    size: A4;
    margin: 20mm;
  }
  * {
    box-sizing: border-box;
  }
  html, body {
    margin: 0;
    padding: 0;
    background: #ffffff;
    color: #222222;
    font-family: Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  h1 { font-size: 22pt; margin: 1em 0 0.5em; color: #111111; page-break-after: avoid; }
  h2 { font-size: 17pt; margin: 1em 0 0.5em; color: #111111; page-break-after: avoid; }
  h3 { font-size: 14pt; margin: 1em 0 0.5em; color: #111111; page-break-after: avoid; }
  p { margin: 0.6em 0; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; page-break-inside: avoid; }
  th, td { border: 1px solid #888888; padding: 6px 10px; text-align: left; }
  th { background: #f3f3f3; }
  blockquote { border-left: 3px solid #bbbbbb; padding-left: 1em; color: #555555; margin: 1em 0; page-break-inside: avoid; }
  ul, ol { margin: 0.6em 0 0.6em 1.5em; padding-left: 1.2em; }
  li { margin: 0.2em 0; }
  img { max-width: 100%; height: auto; page-break-inside: avoid; }
  a { color: #1d4ed8; text-decoration: underline; }
  strong, b { font-weight: bold; }
  em, i { font-style: italic; }
  u { text-decoration: underline; }
  code { font-family: Consolas, Monaco, monospace; background: #f3f3f3; padding: 1px 4px; border-radius: 2px; }
  pre { background: #f3f3f3; padding: 10px; border-radius: 4px; overflow-x: auto; page-break-inside: avoid; }
`;

export default function TiptapEditor({
  content,
  onSave,
  reportId,
  sourceMap,
}: {
  content: any;
  onSave: (json: any) => void;
  reportId: number;
  sourceMap: any;
}) {
  const [saving, setSaving] = useState(false);
  const [exportState, setExport] = useState(false);
  const [selectedSources, setSelectedSources] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const editor = useEditor({
    immediatelyRender: false,
    extensions: editorExtensions,
    content: content,
    onSelectionUpdate: ({ editor }) => {
      const { $from } = editor.state.selection;
      const node = $from.parent;
      const sources = node.attrs?.sources || [];
      if (sourceMap && sources.length > 0) {
        const resolved = sources
          .map((id: string) => sourceMap[id])
          .filter(Boolean);
        setSelectedSources(resolved);
      } else {
        setSelectedSources([]);
      }
    },
  });

  const handleExportPdf = async () => {
    if (!editor || !iframeRef.current) return;
    setExport(true);
    try {
      // 1. Convert Tiptap JSON → clean HTML
      const json = editor.getJSON();
      const html = generateHTML(json, editorExtensions);

      // 2. Write isolated HTML document into iframe
      const iframeDoc =
        iframeRef.current.contentDocument ||
        iframeRef.current.contentWindow?.document;
      if (!iframeDoc) throw new Error("Could not access iframe document");

      iframeDoc.open();
      iframeDoc.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <title>report_${reportId}</title>
            <style>${PDF_STYLES}</style>
          </head>
          <body>${html}</body>
        </html>
      `);
      iframeDoc.close();

      // 3. Wait for images to load
      const images = Array.from(iframeDoc.images);
      await Promise.all(
        images.map(
          (img) =>
            new Promise<void>((resolve) => {
              if (img.complete) resolve();
              else {
                img.onload = () => resolve();
                img.onerror = () => resolve();
              }
            }),
        ),
      );

      // 4. Small delay to ensure layout is fully computed
      await new Promise((r) => setTimeout(r, 200));

      // 5. Trigger browser's print dialog on the iframe
      //    User selects "Save as PDF" as destination
      iframeRef.current.contentWindow?.focus();
      iframeRef.current.contentWindow?.print();
    } catch (err) {
      console.error("PDF export failed:", err);
      alert("Failed to export PDF. Check console for details.");
    } finally {
      setExport(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const json = editor!.getJSON();
      await onSave(json);
    } finally {
      setSaving(false);
    }
  };

  if (!editor) return <div>Loading editor...</div>;

  return (
    <div className="flex gap-4">
      {/* Main editor area */}
      <div className="flex-1">
        {/* Toolbar */}
        <div className="flex flex-wrap gap-1 p-2 border border-gray-300 rounded-t-lg bg-gray-50">
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBold().run()}
            isActive={editor.isActive("bold")}
          >
            B
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleItalic().run()}
            isActive={editor.isActive("italic")}
          >
            I
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            isActive={editor.isActive("underline")}
          >
            U
          </ToolbarButton>

          <div className="w-px bg-gray-300 mx-1" />

          <ToolbarButton
            onClick={() =>
              editor.chain().focus().toggleHeading({ level: 1 }).run()
            }
            isActive={editor.isActive("heading", { level: 1 })}
          >
            H1
          </ToolbarButton>
          <ToolbarButton
            onClick={() =>
              editor.chain().focus().toggleHeading({ level: 2 }).run()
            }
            isActive={editor.isActive("heading", { level: 2 })}
          >
            H2
          </ToolbarButton>
          <ToolbarButton
            onClick={() =>
              editor.chain().focus().toggleHeading({ level: 3 }).run()
            }
            isActive={editor.isActive("heading", { level: 3 })}
          >
            H3
          </ToolbarButton>

          <div className="w-px bg-gray-300 mx-1" />

          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            isActive={editor.isActive("bulletList")}
          >
            List
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            isActive={editor.isActive("orderedList")}
          >
            1. List
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            isActive={editor.isActive("blockquote")}
          >
            Quote
          </ToolbarButton>

          <div className="w-px bg-gray-300 mx-1" />

          <ToolbarButton
            onClick={() =>
              editor
                .chain()
                .focus()
                .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
                .run()
            }
          >
            + Table
          </ToolbarButton>

          <div className="w-px bg-gray-300 mx-1" />

          <ToolbarButton onClick={() => editor.chain().focus().undo().run()}>
            Undo
          </ToolbarButton>
          <ToolbarButton onClick={() => editor.chain().focus().redo().run()}>
            Redo
          </ToolbarButton>

          {/* Save button */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="ml-auto px-4 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            onClick={handleExportPdf}
            disabled={exportState}
            className="px-4 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50"
          >
            {exportState ? "Exporting..." : "Export PDF"}
          </button>
        </div>

        {/* Editor content */}
        <EditorContent
          editor={editor}
          className="border border-t-0 border-gray-300 rounded-b-lg p-4 min-h-[500px] prose max-w-none text-black"
        />
      </div>

      {/* Source panel (right sidebar) */}
      <div className="w-64 border border-gray-300 rounded-lg p-4 h-fit">
        <h3 className="font-semibold text-black text-sm mb-3">Sources</h3>
        {selectedSources.length === 0 ? (
          <p className="text-gray-500 text-sm">
            Click on any block to see its sources
          </p>
        ) : (
          <div className="flex flex-col gap-3">
            {selectedSources.map((src: any, i: number) => (
              <div key={i} className="border rounded p-2 text-sm">
                <p className="font-medium text-black">{src.file_name}</p>
                {src.page !== null && src.page !== undefined && (
                  <p className="text-gray-500">Page {src.page + 1}</p>
                )}
                {src.sheet && (
                  <p className="text-gray-500">Sheet: {src.sheet}</p>
                )}
                {src.section && (
                  <p className="text-gray-500">Section: {src.section}</p>
                )}
                <p>
                  <button
                    onClick={async () => {
                      try {
                        const response = await fetch(
                          `${process.env.NEXT_PUBLIC_API_BASE_URL}/get-attachment-by-s3-key`,
                          {
                            method: "POST",
                            headers: {
                              "Content-Type": "application/json",
                            },
                            credentials: "include",
                            body: JSON.stringify({
                              s3_key: src.s3_key,
                              file_type: src.file_type,
                            }),
                          },
                        );
                        const data = await response.json();
                        console.log("url==>", data);
                        const url = typeof data === "string" ? data : data.url;
                        if (url) setSelectedFile(url);
                      } catch (err) {
                        console.error("Error:", err);
                      }
                    }}
                    className="text-blue-600 hover:underline"
                  >
                    👁
                  </button>
                </p>
              </div>
            ))}
          </div>
        )}
        {selectedFile && (
          <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
            <button
              onClick={() => setSelectedFile(null)}
              className="absolute top-5 right-5 text-white text-2xl"
            >
              ✖
            </button>
            <div className="bg-white w-[80%] h-[80%] rounded-lg overflow-hidden shadow-lg">
              <iframe src={selectedFile} className="w-full h-full" />
            </div>
          </div>
        )}
      </div>

      {/* Hidden iframe for print-to-PDF rendering */}
      <iframe
        ref={iframeRef}
        title="pdf-render"
        style={{
          position: "absolute",
          left: "-9999px",
          top: 0,
          width: "210mm",
          height: "297mm",
          border: "none",
          visibility: "hidden",
        }}
      />
    </div>
  );
}
