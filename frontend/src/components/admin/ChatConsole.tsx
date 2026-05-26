import type { FormEvent } from "react";
import type { ChatMessage } from "@/types";

export function ChatConsole({
  messages,
  input,
  isLoading,
  setInput,
  submitMessage,
}: {
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  setInput: (value: string) => void;
  submitMessage: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <header className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-lg font-semibold">Agentic RAG console</h2>
      </header>
      <div className="max-h-[420px] space-y-3 overflow-y-auto px-4 py-4">
        {messages.map((message, index) => (
          <article
            key={`${message.role}-${index}`}
            className={`rounded-lg px-4 py-3 text-sm leading-6 ${
              message.role === "user"
                ? "ml-8 bg-slate-900 text-white"
                : "mr-8 border border-slate-200 bg-slate-50 text-slate-800"
            }`}
          >
            {message.tool && (
              <div className="mb-2 text-xs font-semibold uppercase text-slate-500">
                {message.tool}
              </div>
            )}
            <p className="whitespace-pre-line">{message.content}</p>
          </article>
        ))}
      </div>
      <form onSubmit={submitMessage} className="border-t border-slate-200 p-4">
        <div className="flex gap-2">
          <input
            className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-3 text-sm"
            placeholder="What are the most common login complaints?"
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            className="rounded-md bg-slate-900 px-4 py-3 text-sm font-semibold text-white disabled:bg-slate-400"
            disabled={isLoading}
          >
            {isLoading ? "Sending" : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}
