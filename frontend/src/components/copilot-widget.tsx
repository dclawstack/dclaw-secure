"use client";

import { useRef, useState } from "react";
import { Bot, Send, Sparkles, X, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { sendChatMessage, type ChatMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function CopilotWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function send() {
    const msg = input.trim();
    if (!msg || sending) return;
    setInput("");
    setSending(true);

    const optimistic: ChatMessage = {
      id: `tmp-${Date.now()}`,
      session_id: sessionId || "",
      role: "user",
      content: msg,
      sources: null,
      created_at: new Date().toISOString(),
    };
    setMessages(m => [...m, optimistic]);
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);

    try {
      const res = await sendChatMessage(msg, sessionId);
      setSessionId(res.session_id);
      setMessages(m => [
        ...m.filter(x => x.id !== optimistic.id),
        { ...optimistic, session_id: res.session_id },
        res.message,
      ]);
    } catch {
      setMessages(m => m.filter(x => x.id !== optimistic.id));
    } finally {
      setSending(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3">
      {open && (
        <div className="flex w-80 flex-col rounded-2xl border bg-background shadow-2xl" style={{ height: "28rem" }}>
          {/* Header */}
          <div className="flex items-center justify-between rounded-t-2xl border-b bg-indigo-600 px-4 py-3">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-white" />
              <span className="text-sm font-semibold text-white">AI Security Copilot</span>
            </div>
            <button onClick={() => setOpen(false)} className="text-white/80 hover:text-white transition-colors">
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-3">
            {messages.length === 0 && (
              <div className="flex flex-1 flex-col items-center justify-center gap-2 text-center">
                <Bot className="h-8 w-8 text-indigo-400 opacity-60" />
                <p className="text-xs text-muted-foreground">Ask anything about your security posture.</p>
              </div>
            )}
            {messages.map(m => {
              const isUser = m.role === "user";
              return (
                <div key={m.id} className={cn("flex gap-2", isUser && "flex-row-reverse")}>
                  <div className={cn("flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs", isUser ? "bg-indigo-600 text-white" : "bg-muted")}>
                    {isUser ? <User className="h-3 w-3" /> : <Bot className="h-3 w-3" />}
                  </div>
                  <div className={cn("max-w-[80%] rounded-xl px-3 py-2 text-xs leading-relaxed", isUser ? "bg-indigo-600 text-white" : "bg-muted text-foreground")}>
                    {m.content}
                  </div>
                </div>
              );
            })}
            {sending && (
              <div className="flex gap-2">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted">
                  <Bot className="h-3 w-3" />
                </div>
                <div className="rounded-xl bg-muted px-3 py-2">
                  <div className="flex gap-1">
                    {[0, 1, 2].map(i => (
                      <span key={i} className="h-1 w-1 rounded-full bg-muted-foreground/50 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={e => { e.preventDefault(); send(); }}
            className="flex gap-2 border-t p-3"
          >
            <Input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={sending}
              className="h-8 text-xs flex-1"
            />
            <Button type="submit" size="icon" disabled={sending || !input.trim()} className="h-8 w-8 shrink-0 bg-indigo-600 hover:bg-indigo-700">
              <Send className="h-3 w-3" />
            </Button>
          </form>
        </div>
      )}

      {/* Toggle button */}
      <button
        onClick={() => setOpen(o => !o)}
        className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg hover:bg-indigo-700 transition-colors"
        aria-label="Toggle AI Copilot"
      >
        {open ? <X className="h-5 w-5" /> : <Sparkles className="h-5 w-5" />}
      </button>
    </div>
  );
}
