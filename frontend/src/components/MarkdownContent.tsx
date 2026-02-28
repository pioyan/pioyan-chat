"use client";
/** Renders message content as GitHub-Flavored Markdown. */

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  content: string;
  ownMessage?: boolean;
}

export default function MarkdownContent({ content, ownMessage }: Props) {
  return (
    <div
      className={`markdown-content text-sm break-words ${
        ownMessage
          ? "text-white own-message"
          : "text-gray-800 dark:text-gray-200"
      }`}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
