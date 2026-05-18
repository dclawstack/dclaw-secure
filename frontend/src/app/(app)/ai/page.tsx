"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Send, User, AlertCircle, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { sendChatMessage, type ChatMessage } from "@/lib/api";

const SUGGESTED = [
  "What are my top critical vulnerabilities?",
  "What's my SOC2 compliance status?",
  "Which policies haven't been acknowledged?",
  "Show me assets with the highest risk scores.",
];

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${isUser ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${isUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"}`}>
        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
        <p className={`mt-1 text-xs opacity-60`}>
          {new Date(msg.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

export default function AIPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(text?: string) {
    const msg = (text ?? input).trim();
    if (!msg || sending) return;
    setInput("");
    setError(null);
    setSending(true);

    // Optimistic user message
    const optimistic: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: sessionId || "",
      role: "user",
      content: msg,
      sources: null,
      created_at: new Date().toISOString(),
    };
    setMessages(m => [...m, optimistic]);

    try {
      const res = await sendChatMessage(msg, sessionId);
      setSessionId(res.session_id);
      // Replace optimistic with real, then add assistant
      setMessages(m => [
        ...m.filter(x => x.id !== optimistic.id),
        { ...optimistic, session_id: res.session_id },
        res.message,
      ]);
    } catch (e: any) {
      setMessages(m => m.filter(x => x.id !== optimistic.id));
      setError(e.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col" style={{ height: "calc(100vh - 8rem)" }}>
      <div className="mb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-indigo-500" />
          AI Security Copilot
        </h1>
        <p className="text-sm text-muted-foreground">Ask questions about your security posture using real data.</p>
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden">
        {/* Messages area */}
        <CardContent className="flex flex-1 flex-col overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="flex flex-1 flex-col items-center justify-center gap-4 text-center">
              <Bot className="h-12 w-12 text-indigo-400 opacity-60" />
              <div>
                <p className="font-medium">Your AI security analyst</p>
                <p className="text-sm text-muted-foreground">Ask about vulnerabilities, compliance, policies, or anything security-related.</p>
              </div>
              <div className="grid grid-cols-1 gap-2 w-full max-w-md">
                {SUGGESTED.map(q => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="rounded-lg border border-border bg-background px-3 py-2 text-left text-sm hover:bg-muted transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map(m => <MessageBubble key={m.id} msg={m} />)}
              {sending && (
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="rounded-2xl bg-muted px-4 py-3">
                    <div className="flex gap-1">
                      {[0, 1, 2].map(i => (
                        <span key={i} className="h-1.5 w-1.5 rounded-full bg-muted-foreground/50 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </CardContent>

        {/* Input area */}
        <div className="border-t p-4">
          {error && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />{error}
            </div>
          )}
          <form
            onSubmit={e => { e.preventDefault(); send(); }}
            className="flex gap-2"
          >
            <Input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask about your security posture..."
              disabled={sending}
              className="flex-1"
            />
            <Button type="submit" disabled={sending || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
