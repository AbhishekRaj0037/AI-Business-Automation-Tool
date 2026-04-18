"use client";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Table } from "@tiptap/extension-table";
import TableRow from "@tiptap/extension-table-row";
import TableHeader from "@tiptap/extension-table-header";
import TableCell from "@tiptap/extension-table-cell";
import ImageExtension from "@tiptap/extension-image";
import Underline from "@tiptap/extension-underline";
import Placeholder from "@tiptap/extension-placeholder";
import { useState } from "react";
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

// Extend Paragraph to accept sources
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

// Extend Heading to accept sources
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
  const [selectedSources, setSelectedSources] = useState<any[]>([]);

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({
        heading: false, // disable default heading
        paragraph: false, // disable default paragraph
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
    ],
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

  if (!editor) return <div>Loading editor...</div>;

  const handleSave = async () => {
    setSaving(true);
    try {
      const json = editor.getJSON();
      await onSave(json);
    } finally {
      setSaving(false);
    }
  };

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
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
