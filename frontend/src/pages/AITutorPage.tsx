import React, { useState, useRef, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import {
  Sparkles,
  Send,
  HelpCircle,
  Bot,
  User as UserIcon,
  Plus,
  RotateCcw,
  Copy,
  Check,
  Lightbulb,
  AlertCircle,
  BookOpen,
} from "lucide-react";
import { useToast } from "@/components/ui/Toast";

interface AITutorPageProps {
  onNavigate: (tab: any, params?: any) => void;
}

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  content: string;
  isError?: boolean;
}

const STARTER_PROMPTS = [
  "Explain the core concept in simple terms (ELI5)",
  "What are common exam traps & pitfalls?",
  "Give me a practical step-by-step example",
  "Compare and contrast the main mechanisms",
];

const formatInline = (text: string): React.ReactNode => {
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="font-semibold text-[#1F2A24]">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={i} className="italic text-[#2F5D46]">{part.slice(1, -1)}</em>;
    }
    return part;
  });
};

const renderFormattedText = (content: string) => {
  if (!content) return null;
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (trimmed.startsWith("### ")) {
      elements.push(
        <h4 key={idx} className="font-bold text-sm sm:text-base text-[#1F2A24] mt-2 mb-1">
          {formatInline(trimmed.substring(4))}
        </h4>
      );
    } else if (trimmed.startsWith("## ")) {
      elements.push(
        <h3 key={idx} className="font-bold text-base text-[#1F2A24] mt-2.5 mb-1 pb-0.5 border-b border-[#E3E8E2]">
          {formatInline(trimmed.substring(3))}
        </h3>
      );
    } else if (trimmed.startsWith("# ")) {
      elements.push(
        <h2 key={idx} className="font-bold text-lg text-[#1F2A24] mt-3 mb-1 pb-1 border-b border-[#E3E8E2]">
          {formatInline(trimmed.substring(2))}
        </h2>
      );
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      elements.push(
        <div key={idx} className="flex items-start gap-2 my-0.5 ml-1">
          <span className="text-[#2F5D46] font-bold">•</span>
          <span className="text-[#1F2A24]">{formatInline(trimmed.substring(2))}</span>
        </div>
      );
    } else if (/^\d+\.\s/.test(trimmed)) {
      const match = trimmed.match(/^(\d+\.)\s(.*)$/);
      elements.push(
        <div key={idx} className="flex items-start gap-2 my-1 ml-1">
          <span className="font-semibold text-[#2F5D46] shrink-0">{match ? match[1] : "•"}</span>
          <span className="text-[#1F2A24]">{formatInline(match ? match[2] : trimmed)}</span>
        </div>
      );
    } else if (trimmed.startsWith("> ")) {
      elements.push(
        <blockquote key={idx} className="border-l-2 border-[#2F5D46] pl-3 italic text-[#607166] my-2 bg-[#EBF2EC]/40 py-1 rounded-r">
          {formatInline(trimmed.substring(2))}
        </blockquote>
      );
    } else if (trimmed === "---") {
      elements.push(<hr key={idx} className="my-2 border-[#E3E8E2]" />);
    } else if (!trimmed) {
      elements.push(<div key={idx} className="h-1.5" />);
    } else {
      elements.push(
        <p key={idx} className="my-0.5 text-[#1F2A24]">
          {formatInline(line)}
        </p>
      );
    }
  });

  return <div className="space-y-0.5 leading-relaxed">{elements}</div>;
};

export const AITutorPage: React.FC<AITutorPageProps> = ({ onNavigate }) => {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [activeConvId, setActiveConvId] = useState<number | null>(null);
  const [tutoringMode, setTutoringMode] = useState<"standard" | "eli5" | "deeper">("standard");
  const [inputMessage, setInputMessage] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Mini quiz "Check my understanding" state
  const [miniQuizOpen, setMiniQuizOpen] = useState(false);
  const [miniQuizLoading, setMiniQuizLoading] = useState(false);
  const [miniQuizData, setMiniQuizData] = useState<any | null>(null);
  const [miniQuizSelected, setMiniQuizSelected] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load subjects
  const { data: subjectsData } = useQuery({
    queryKey: ["subjects"],
    queryFn: () => api.subjects.list({ page_size: 50 }),
  });
  const subjects = subjectsData?.items || [];
  const activeSubjectId = selectedSubjectId || (subjects.length > 0 ? subjects[0].id : null);

  // Load topics for active subject
  const { data: topicsData } = useQuery({
    queryKey: ["topics", activeSubjectId],
    queryFn: () => (activeSubjectId ? api.topics.listForSubject(activeSubjectId) : null),
    enabled: !!activeSubjectId,
  });
  const topics = topicsData?.items || [];
  const activeTopicId = selectedTopicId || (topics.length > 0 ? topics[0].id : null);

  // Load past conversations
  const { data: conversations, refetch: refetchConversations } = useQuery({
    queryKey: ["tutor-conversations", activeTopicId],
    queryFn: () => api.tutor.listConversations(activeTopicId || undefined),
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [messages]);

  const handleStartNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setInputMessage("");
  };

  const handleCopyMessage = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    showToast("Copied to clipboard", "success");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSendMessage = async (overrideText?: string) => {
    const textToSend = (overrideText || inputMessage).trim();
    if (!textToSend || isStreaming) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      content: textToSend,
    };
    setMessages((prev) => [...prev, userMsg]);
    if (!overrideText) setInputMessage("");
    setIsStreaming(true);

    const assistantMsgId = (Date.now() + 1).toString();
    setMessages((prev) => [...prev, { id: assistantMsgId, sender: "assistant", content: "" }]);

    try {
      await api.tutor.streamChat(
        {
          topic_id: activeTopicId || undefined,
          message: textToSend,
          mode: tutoringMode,
          conversation_id: activeConvId || undefined,
        },
        (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId ? { ...m, content: m.content + token } : m
            )
          );
        },
        (newConvId) => {
          setActiveConvId(newConvId);
          refetchConversations();
          queryClient.invalidateQueries({ queryKey: ["subjects"] });
          queryClient.invalidateQueries({ queryKey: ["topics"] });
        }
      );
    } catch (err: any) {
      const errMsg = err?.message || "Chat streaming failed. Please check your connection.";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsgId
            ? {
                ...m,
                content: `⚠️ ${errMsg}`,
                isError: true,
              }
            : m
        )
      );
      showToast(errMsg, "error");
    } finally {
      setIsStreaming(false);
    }
  };

  const handleCheckUnderstanding = async () => {
    setMiniQuizLoading(true);
    try {
      const q = await api.tutor.checkUnderstanding({
        topic_id: activeTopicId || undefined,
      });
      setMiniQuizData(q);
      setMiniQuizSelected(null);
      setMiniQuizOpen(true);
    } catch (err: any) {
      showToast(err?.message || "Failed to generate mini-quiz", "error");
    } finally {
      setMiniQuizLoading(false);
    }
  };

  const handleSelectConversation = async (convId: number) => {
    setActiveConvId(convId);
    try {
      const conv = await api.tutor.getConversation(convId);
      setMessages(
        conv.messages.map((m) => ({
          id: m.id.toString(),
          sender: m.sender,
          content: m.content,
        }))
      );
    } catch (err) {
      showToast("Failed to load conversation", "error");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold text-[#2F5D46] tracking-wider uppercase flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Socratic AI Companion
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1F2A24] tracking-tight mt-1 font-serif">
            AI Tutor
          </h1>
          <p className="text-sm text-[#607166] mt-1">
            Grounded step-by-step reasoning tutor citing your uploaded materials.
          </p>
        </div>

        {/* Action Controls & Selectors */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Subject Dropdown */}
          {subjects.length > 0 && (
            <select
              value={activeSubjectId || ""}
              onChange={(e) => {
                const subId = Number(e.target.value);
                setSelectedSubjectId(subId);
                setSelectedTopicId(null);
                setMessages([]);
                setActiveConvId(null);
              }}
              className="text-xs px-3 py-2 rounded-xl bg-white border border-[#E3E8E2] text-[#1F2A24] font-medium shadow-2xs"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          )}

          {/* Topic Dropdown */}
          {topics.length > 0 && (
            <select
              value={activeTopicId || ""}
              onChange={(e) => {
                setSelectedTopicId(Number(e.target.value));
                setMessages([]);
                setActiveConvId(null);
              }}
              className="text-xs px-3 py-2 rounded-xl bg-white border border-[#E3E8E2] text-[#1F2A24] shadow-2xs"
            >
              {topics.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={handleStartNewChat}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white hover:bg-[#F4F6F1] text-[#1F2A24] text-xs font-medium border border-[#E3E8E2] transition-colors shadow-2xs"
            title="Start new conversation"
          >
            <Plus className="w-3.5 h-3.5 text-[#2F5D46]" />
            <span>New Chat</span>
          </button>

          <button
            onClick={handleCheckUnderstanding}
            disabled={miniQuizLoading}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-medium border border-emerald-200 transition-colors shadow-2xs disabled:opacity-50"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>{miniQuizLoading ? "Generating..." : "Check My Understanding"}</span>
          </button>
        </div>
      </div>

      {/* Mini Quiz Modal */}
      {miniQuizOpen && miniQuizData && (
        <div className="p-6 bg-white rounded-2xl border border-[#2F5D46] shadow-md space-y-4 animate-fade-in">
          <div className="flex items-center justify-between border-b border-[#E3E8E2] pb-3">
            <h3 className="text-sm font-semibold text-[#1F2A24] flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#2F5D46]" />
              <span>Quick Understanding Check</span>
            </h3>
            <button
              onClick={() => setMiniQuizOpen(false)}
              className="text-xs text-[#607166] hover:text-[#1F2A24] font-medium px-2 py-1 rounded-lg hover:bg-[#F4F6F1]"
            >
              Close
            </button>
          </div>

          <p className="text-sm font-semibold text-[#1F2A24]">{miniQuizData.question_text}</p>

          {miniQuizData.options && (
            <div className="space-y-2">
              {miniQuizData.options.map((opt: string, i: number) => {
                const isSelected = miniQuizSelected === opt;
                const isCorrect = opt === miniQuizData.correct_answer;
                return (
                  <button
                    key={i}
                    onClick={() => setMiniQuizSelected(opt)}
                    className={`w-full p-3 rounded-xl text-xs text-left border transition-all ${
                      miniQuizSelected
                        ? isCorrect
                          ? "bg-emerald-50 border-emerald-500 font-semibold text-emerald-900"
                          : isSelected
                          ? "bg-rose-50 border-rose-500 text-rose-900"
                          : "bg-white border-[#E3E8E2] text-[#607166]"
                        : "bg-white border-[#E3E8E2] hover:bg-[#F4F6F1] text-[#1F2A24]"
                    }`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          )}

          {miniQuizSelected && (
            <div className="p-3 rounded-xl bg-[#F4F6F1] text-xs text-[#1F2A24] space-y-1">
              <p className="font-medium">💡 Explanation:</p>
              <p className="italic text-[#607166]">{miniQuizData.explanation}</p>
              {miniQuizData.citation && (
                <p className="text-[11px] text-[#2F5D46] font-mono mt-1">
                  Citation: {miniQuizData.citation}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Main Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Chat History List (3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-2xl border border-[#E3E8E2] p-4 space-y-3 shadow-2xs">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-[#1F2A24] uppercase tracking-wider">
              Past Conversations
            </h3>
            <button
              onClick={handleStartNewChat}
              className="p-1 rounded-lg hover:bg-[#F4F6F1] text-[#2F5D46]"
              title="New Chat"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
            {conversations && conversations.length > 0 ? (
              conversations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => handleSelectConversation(c.id)}
                  className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-all ${
                    activeConvId === c.id
                      ? "bg-[#EBF2EC] border-[#2F5D46] font-semibold text-[#2F5D46]"
                      : "bg-white border-[#E3E8E2] hover:bg-[#F4F6F1] text-[#1F2A24]"
                  }`}
                >
                  <p className="line-clamp-1">{c.title}</p>
                  <span className="text-[10px] text-[#8C9B90] mt-1 block">
                    {new Date(c.updated_at).toLocaleDateString()}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-6 text-xs text-[#8C9B90]">
                <p>No conversations yet.</p>
                <p className="text-[11px] mt-1 text-[#607166]">Ask a question to start tutoring!</p>
              </div>
            )}
          </div>
        </div>

        {/* Right: Live Chat Window (9 cols) */}
        <div className="lg:col-span-9 bg-white rounded-2xl border border-[#E3E8E2] flex flex-col h-[620px] overflow-hidden shadow-2xs">
          {/* Chat Mode Control Bar */}
          <div className="p-3 border-b border-[#E3E8E2] bg-[#F4F6F1]/50 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[#607166]">Tutoring Mode:</span>
              <div className="flex gap-1.5">
                {(["standard", "eli5", "deeper"] as const).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setTutoringMode(mode)}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                      tutoringMode === mode
                        ? "bg-[#2F5D46] text-white shadow-2xs"
                        : "bg-white text-[#607166] hover:bg-[#EBF2EC] border border-[#E3E8E2]"
                    }`}
                  >
                    {mode === "standard" && "Standard"}
                    {mode === "eli5" && "ELI5 (Simple)"}
                    {mode === "deeper" && "Deep Dive"}
                  </button>
                ))}
              </div>
            </div>

            {activeConvId && (
              <button
                onClick={handleStartNewChat}
                className="text-xs text-[#607166] hover:text-[#2F5D46] inline-flex items-center gap-1 font-medium"
              >
                <RotateCcw className="w-3 h-3" /> Clear Chat
              </button>
            )}
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-[#8C9B90] space-y-4 max-w-md mx-auto">
                <div className="w-14 h-14 rounded-2xl bg-[#EBF2EC] flex items-center justify-center text-[#2F5D46]">
                  <Bot className="w-8 h-8" />
                </div>
                <div>
                  <p className="text-base font-semibold text-[#1F2A24]">
                    StudyPilot Socratic Tutor is ready
                  </p>
                  <p className="text-xs text-[#607166] mt-1">
                    Ask questions regarding concepts, formulas, or past exam problems grounded in your syllabus.
                  </p>
                </div>

                {/* Starter Prompts Pills */}
                <div className="w-full space-y-2 pt-2">
                  <p className="text-[11px] font-semibold text-[#8C9B90] uppercase tracking-wider text-left">
                    Suggested prompts:
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                    {STARTER_PROMPTS.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(prompt)}
                        className="p-2.5 rounded-xl bg-[#F4F6F1] hover:bg-[#EBF2EC] text-xs text-[#1F2A24] border border-[#E3E8E2] text-left transition-all hover:border-[#2F5D46] flex items-start gap-2 group"
                      >
                        <Lightbulb className="w-3.5 h-3.5 text-[#2F5D46] shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                        <span className="line-clamp-2">{prompt}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-3 ${m.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  {m.sender === "assistant" && (
                    <div className="w-7 h-7 rounded-lg bg-[#2F5D46] text-white flex items-center justify-center shrink-0 text-xs font-bold shadow-2xs">
                      S
                    </div>
                  )}
                  <div className="relative group max-w-[85%]">
                    <div
                      className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                        m.sender === "user"
                          ? "bg-[#2F5D46] text-white rounded-br-none shadow-2xs whitespace-pre-wrap"
                          : m.isError
                          ? "bg-rose-50 border border-rose-200 text-rose-800 rounded-bl-none whitespace-pre-wrap"
                          : "bg-[#F4F6F1] text-[#1F2A24] rounded-bl-none border border-[#E3E8E2]"
                      }`}
                    >
                      {m.content ? (
                        m.sender === "assistant" && !m.isError ? (
                          renderFormattedText(m.content)
                        ) : (
                          m.content
                        )
                      ) : (
                        <div className="flex items-center gap-2 text-[#607166]">
                          <span className="inline-block animate-pulse">Thinking & citing materials...</span>
                        </div>
                      )}
                    </div>

                    {/* Copy Button for assistant answers */}
                    {m.sender === "assistant" && m.content && !m.isError && (
                      <button
                        onClick={() => handleCopyMessage(m.id, m.content)}
                        className="absolute top-2 right-2 p-1 rounded-md bg-white/80 hover:bg-white text-[#607166] opacity-0 group-hover:opacity-100 transition-opacity border border-[#E3E8E2]"
                        title="Copy message"
                      >
                        {copiedId === m.id ? (
                          <Check className="w-3 h-3 text-emerald-600" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 border-t border-[#E3E8E2] bg-white flex gap-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask anything about this topic or syllabus..."
              disabled={isStreaming}
              className="flex-1 text-xs sm:text-sm px-4 py-2.5 rounded-xl bg-[#F4F6F1] border border-[#E3E8E2] text-[#1F2A24] focus:outline-none focus:ring-2 focus:ring-[#2F5D46] transition-all"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isStreaming}
              className="p-2.5 px-4 rounded-xl bg-[#2F5D46] text-white hover:bg-[#254A37] transition-all disabled:opacity-50 shrink-0 flex items-center gap-1.5 shadow-2xs font-medium text-xs"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
