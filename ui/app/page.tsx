"use client";

import { useState, useRef, useEffect } from "react";

const RESEARCH_QUESTIONS = [
  "What kinds of old photos do users struggle to retrieve?",
  "What information do people actually remember about a photo?",
  "What information have they forgotten?",
  "How do users formulate searches when their memory is incomplete?",
  "Which retrieval problem is the biggest opportunity area?",
  "What workarounds do users try when search fails?",
  "Why do users fail to find screenshots and documents?",
  "How often do face recognition failures prevent users from finding people?",
  "What is the impact of Ask Photos / Gemini updates on search?",
];

function parseInline(text: string): React.ReactNode[] {
  if (!text) return [];

  const nodes: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // 1. Check for inline code `code`
    const codeMatch = remaining.match(/^`([^`]+)`/);
    if (codeMatch) {
      nodes.push(
        <code
          key={key++}
          className="bg-gray-200/70 text-blue-700 px-1.5 py-0.5 rounded text-[13px] font-mono font-medium"
        >
          {codeMatch[1]}
        </code>
      );
      remaining = remaining.slice(codeMatch[0].length);
      continue;
    }

    // 2. Check for bold **text**
    const boldMatch = remaining.match(/^\*\*([^*]+)\*\*/);
    if (boldMatch) {
      nodes.push(
        <strong key={key++} className="font-semibold text-gray-900">
          {boldMatch[1]}
        </strong>
      );
      remaining = remaining.slice(boldMatch[0].length);
      continue;
    }

    // 3. Check for incomplete bold at end of string (e.g. streaming chunks): **text
    const incompleteBoldMatch = remaining.match(/^\*\*([^*]+)$/);
    if (incompleteBoldMatch) {
      nodes.push(
        <strong key={key++} className="font-semibold text-gray-900">
          {incompleteBoldMatch[1]}
        </strong>
      );
      break;
    }

    // 4. Check for italic *text*
    const italicMatch = remaining.match(/^\*([^*]+)\*/);
    if (italicMatch) {
      nodes.push(
        <em key={key++} className="italic text-gray-800">
          {italicMatch[1]}
        </em>
      );
      remaining = remaining.slice(italicMatch[0].length);
      continue;
    }

    // 5. Find next special character ` or *
    const nextSpecial = remaining.search(/[`*]/);
    if (nextSpecial === -1) {
      nodes.push(remaining);
      break;
    } else if (nextSpecial === 0) {
      // Lone special delimiter or partial delimiter during streaming
      if (remaining === "**") {
        break; // suppress dangling asterisks during stream
      }
      nodes.push(remaining[0]);
      remaining = remaining.slice(1);
    } else {
      nodes.push(remaining.slice(0, nextSpecial));
      remaining = remaining.slice(nextSpecial);
    }
  }

  return nodes;
}

function FormattedMessage({ content }: { content: string }) {
  if (!content) return null;

  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];
  let listType: "ul" | "ol" | null = null;
  let currentPara: string[] = [];

  const flushList = () => {
    if (currentList.length > 0 && listType) {
      if (listType === "ul") {
        elements.push(
          <ul key={`ul-${elements.length}`} className="my-2.5 space-y-1.5 pl-0.5">
            {currentList}
          </ul>
        );
      } else {
        elements.push(
          <ol key={`ol-${elements.length}`} className="my-2.5 space-y-1.5 pl-0.5">
            {currentList}
          </ol>
        );
      }
      currentList = [];
      listType = null;
    }
  };

  const flushPara = () => {
    if (currentPara.length > 0) {
      const text = currentPara.join(" ");
      elements.push(
        <p
          key={`p-${elements.length}`}
          className="my-1.5 first:mt-0 last:mb-0 text-[14.5px] leading-relaxed text-gray-800"
        >
          {parseInline(text)}
        </p>
      );
      currentPara = [];
    }
  };

  lines.forEach((rawLine, idx) => {
    const trimmed = rawLine.trim();

    if (!trimmed) {
      flushPara();
      flushList();
      return;
    }

    // Heading: ### or ## or #
    const headingMatch = rawLine.match(/^(\s*)(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      flushPara();
      flushList();
      const level = headingMatch[2].length;
      elements.push(
        <div
          key={`h-${idx}`}
          className={`font-semibold text-gray-900 ${
            level === 1 ? "text-base mt-3 mb-1.5 font-bold" : "text-[14.5px] mt-2.5 mb-1"
          }`}
        >
          {parseInline(headingMatch[3])}
        </div>
      );
      return;
    }

    // Bullet list item: - item, * item, • item
    const bulletMatch = rawLine.match(/^(\s*)[-*•]\s+(.*)$/);
    if (bulletMatch) {
      flushPara();
      if (listType !== "ul") {
        flushList();
        listType = "ul";
      }
      currentList.push(
        <li
          key={`li-${idx}`}
          className="flex items-start gap-2.5 text-[14px] leading-relaxed text-gray-800"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-2 shrink-0" />
          <span className="flex-1">{parseInline(bulletMatch[2])}</span>
        </li>
      );
      return;
    }

    // Numbered list item: 1. item, 2. item
    const numberedMatch = rawLine.match(/^(\s*)(\d+)\.\s+(.*)$/);
    if (numberedMatch) {
      flushPara();
      if (listType !== "ol") {
        flushList();
        listType = "ol";
      }
      currentList.push(
        <li
          key={`ol-li-${idx}`}
          className="flex items-start gap-2 text-[14px] leading-relaxed text-gray-800"
        >
          <span className="font-bold text-blue-700 shrink-0 text-xs mt-0.5">
            {numberedMatch[2]}.
          </span>
          <span className="flex-1">{parseInline(numberedMatch[3])}</span>
        </li>
      );
      return;
    }

    // Regular line in paragraph
    currentPara.push(trimmed);
  });

  flushPara();
  flushList();

  return <div className="space-y-1">{elements}</div>;
}

export default function AskAssistantPage() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text: string = input) => {
    if (!text.trim() || isLoading) return;
    const userQuery = text.trim();
    setMessages((prev) => [...prev, { role: "user", content: userQuery }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery, stream: true }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || "Failed to fetch response");
      }

      const contentType = res.headers.get("content-type") || "";

      if (contentType.includes("text/event-stream") && res.body) {
        // Append empty assistant message to update incrementally
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let accumulated = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const dataStr = line.slice(6).trim();
              if (dataStr === "[DONE]") break;
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.text) {
                  accumulated += parsed.text;
                  const clean = accumulated
                    .replace(/\b(\d+)\s+items\b/gi, "$1 reviews")
                    .replace(/\bitems\b/gi, "reviews")
                    .replace(/\bitem\b/gi, "review");

                  setMessages((prev) => {
                    const next = [...prev];
                    next[next.length - 1] = {
                      role: "assistant",
                      content: clean,
                    };
                    return next;
                  });
                }
              } catch {
                // Ignore partial json parse errors in streaming
              }
            }
          }
        }
      } else {
        // Fallback for regular JSON
        const data = await res.json();
        const cleanText = (data.content || JSON.stringify(data))
          .replace(/\b(\d+)\s+items\b/gi, "$1 reviews")
          .replace(/\bitems\b/gi, "reviews")
          .replace(/\bitem\b/gi, "review");

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: cleanText,
          },
        ]);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (isLoading) return;
    setMessages([]);
    setInput("");
  };

  const userQuestionCount = messages.filter((m) => m.role === "user").length;

  return (
    <div className="max-w-4xl mx-auto pt-2 sm:pt-6 pb-12">
      <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm flex flex-col min-h-[580px]">
        
        {/* TOP HEADER BAR */}
        <div className="px-4 sm:px-6 py-3.5 border-b border-gray-100 flex items-center justify-between bg-white">
          <div className="text-xs font-semibold text-gray-500 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600"></span>
            {userQuestionCount > 0
              ? `${userQuestionCount} question${userQuestionCount === 1 ? "" : "s"} asked`
              : "Google Photos Retrieval Assistant"}
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              disabled={isLoading}
              className="border border-gray-200 rounded-full px-3.5 py-1 text-xs font-semibold text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors disabled:opacity-40"
            >
              Clear chat
            </button>
          )}
        </div>

        {/* CHAT MESSAGES AREA */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 sm:space-y-5">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col justify-center items-center text-center py-10 sm:py-16 px-2 sm:px-4">
              <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-1">Ask the Discovery Engine</h3>
              <p className="text-xs text-gray-500 max-w-md mb-6">
                Data-backed answers extracted from 4,615 analyzed user reviews. Click a suggested question below or type your own.
              </p>

              <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
                {RESEARCH_QUESTIONS.slice(0, 5).map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(q)}
                    disabled={isLoading}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-full text-xs font-medium text-gray-700 hover:border-blue-300 hover:bg-blue-50/50 hover:text-blue-700 transition-all shadow-2xs"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, i) => {
              const isUser = msg.role === "user";
              const isError = !isUser && msg.content.startsWith("Error:");

              return (
                <div
                  key={i}
                  className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] text-[14.5px] leading-relaxed shadow-2xs ${
                      isUser
                        ? "bg-[#1A73E8] text-white font-medium px-5 py-3 rounded-2xl rounded-tr-xs whitespace-pre-wrap"
                        : isError
                        ? "bg-red-50 text-red-700 border border-red-200 px-5 py-4 rounded-2xl whitespace-pre-wrap"
                        : "bg-[#F8FAFC] text-[#1F2937] border border-[#E2E8F0] px-5 py-4 rounded-2xl rounded-tl-xs font-normal"
                    }`}
                  >
                    {isUser || isError ? (
                      msg.content
                    ) : (
                      <FormattedMessage content={msg.content} />
                    )}
                  </div>
                </div>
              );
            })
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[#F8FAFC] border border-[#E2E8F0] text-blue-600 px-5 py-3.5 rounded-2xl rounded-tl-xs flex items-center gap-1.5 shadow-2xs">
                <span className="w-2 h-2 rounded-full bg-[#1A73E8] animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-[#1A73E8] animate-bounce" style={{ animationDelay: "0.2s" }}></span>
                <span className="w-2 h-2 rounded-full bg-[#1A73E8] animate-bounce" style={{ animationDelay: "0.4s" }}></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* BOTTOM SECTION: MORE QUESTIONS CHIPS + INPUT BAR */}
        <div className="p-4 border-t border-gray-100 bg-white space-y-3">
          
          {/* "More questions:" Horizontal Scroll Row */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider shrink-0">
              More questions:
            </span>
            <div className="flex gap-2">
              {RESEARCH_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  disabled={isLoading}
                  className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs font-medium text-gray-700 hover:border-blue-400 hover:bg-blue-50/60 hover:text-blue-700 whitespace-nowrap transition-all shadow-2xs shrink-0 cursor-pointer disabled:opacity-40"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Pill Input Container */}
          <div className="border border-gray-200 rounded-full p-1.5 flex items-center bg-white shadow-xs focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
            <input
              type="text"
              disabled={isLoading}
              className="flex-1 px-4 py-1.5 text-sm text-gray-800 placeholder-gray-400 bg-transparent focus:outline-none disabled:opacity-50"
              placeholder={isLoading ? "Analyzing reviews..." : "Ask about photo search failures, workarounds, missing metadata..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button
              disabled={isLoading || !input.trim()}
              className="bg-[#1A73E8] hover:bg-[#1557B0] text-white font-bold px-6 py-2 rounded-full text-xs shadow-xs transition-all disabled:opacity-40 disabled:bg-blue-200 cursor-pointer disabled:cursor-not-allowed"
              onClick={() => handleSend()}
            >
              Send
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
