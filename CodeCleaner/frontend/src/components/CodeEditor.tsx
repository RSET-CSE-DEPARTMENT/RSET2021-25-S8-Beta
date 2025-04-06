import React, { useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";
import { EditorProps } from "../types";

export const CodeEditor: React.FC<EditorProps> = ({
  code = "// Your code here", // Ensure default value
  onChange,
  language = "java",
  theme,
}) => {
  const editorRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const resizeObserver = useRef<ResizeObserver | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      resizeObserver.current = new ResizeObserver(() => {
        requestAnimationFrame(() => {
          if (editorRef.current) {
            editorRef.current.layout(); // Ensure layout update
          }
        });
      });

      resizeObserver.current.observe(containerRef.current);
    }

    return () => {
      resizeObserver.current?.disconnect();
      editorRef.current?.dispose();
    };
  }, []);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
    editor.getModel()?.updateOptions({ tabSize: 2 });
    editor.layout(); // Ensure it lays out properly on mount
  };

  console.log("Code passed to editor:", code); // Debugging

  return (
    <div
      ref={containerRef}
      className="h-full w-full rounded overflow-hidden flex flex-col z-100 bg-transparent"    >
      <Editor
        height="100%"
        defaultLanguage={language}
        value={code}
        onChange={(value) => onChange(value || "")}
        theme={theme === "dark" ? "vs-dark" : "light"}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: true },
          fontSize: 14,
          wordWrap: "on",
          automaticLayout: true, // Fixes rendering issue
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          roundedSelection: false,
          scrollbar: {
            horizontal: "visible",
            vertical: "visible",
            alwaysConsumeMouseWheel: false,
          },
          padding: { top: 10 },
          tabSize: 2,
          renderWhitespace: "selection",
          smoothScrolling: true,
          cursorBlinking: "smooth",
          cursorSmoothCaretAnimation: "on",
        }}
      />
    </div>
  );
};
