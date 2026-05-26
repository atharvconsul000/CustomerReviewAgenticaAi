"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import type { Data, Layout } from "plotly.js";
import { AdminDashboard } from "@/components/admin/AdminDashboard";
import { AuthPanel } from "@/components/auth/AuthPanel";
import { CustomerPortal } from "@/components/reviews/CustomerPortal";
import { API_BASE, authHeaders } from "@/lib/api";
import type { Analysis, ChatMessage, PlotPoint, Review, User } from "@/types";

const palette: Record<string, string> = {
  Billing: "#2563eb",
  Login: "#dc2626",
  Performance: "#16a34a",
  "Feature Request": "#9333ea",
  "Data Sync": "#d97706",
};

export default function Home() {
  const [token, setToken] = useState(() =>
    typeof window === "undefined"
      ? ""
      : localStorage.getItem("support-analyzer-token") ?? "",
  );
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [authForm, setAuthForm] = useState({
    name: "",
    email: "admin@example.com",
    password: "admin123",
  });
  const [reviews, setReviews] = useState<Review[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    category: "Login",
    comment: "",
  });
  const [points, setPoints] = useState<PlotPoint[]>([]);
  const [meta, setMeta] = useState({ tickets: 0, embedding_dimensions: 768 });
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Ask for support insights, risks, themes, or counts. Try: What should we fix first for login users?",
      tool: "Admin AI Ready",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (!token || user) return;

    async function loadSession() {
      try {
        const response = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error("Session expired");
        setUser(await response.json());
      } catch {
        logout();
      }
    }

    loadSession();
  }, [token, user]);

  useEffect(() => {
    if (!token || !user) return;
    loadReviews(token, user.role);
    if (user.role === "admin") loadAdminData(token);
  }, [token, user]);

  async function loadReviews(activeToken: string, role: User["role"]) {
    const endpoint = role === "admin" ? "/admin/reviews" : "/reviews";
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { Authorization: `Bearer ${activeToken}` },
    });
    if (response.ok) setReviews(await response.json());
  }

  async function loadAdminData(activeToken: string) {
    const [plotResponse, analysisResponse] = await Promise.all([
      fetch(`${API_BASE}/plot-data`, {
        headers: { Authorization: `Bearer ${activeToken}` },
      }),
      fetch(`${API_BASE}/admin/reviews/analysis`, {
        headers: { Authorization: `Bearer ${activeToken}` },
      }),
    ]);

    if (plotResponse.ok) {
      const payload = await plotResponse.json();
      setPoints(payload.data);
      setMeta(payload.meta);
    }
    if (analysisResponse.ok) setAnalysis(await analysisResponse.json());
  }

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("");
    const endpoint = authMode === "login" ? "/auth/login" : "/auth/signup";
    const body =
      authMode === "login"
        ? { email: authForm.email, password: authForm.password }
        : authForm;

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.detail ?? "Authentication failed");
      }
      const payload = await response.json();
      localStorage.setItem("support-analyzer-token", payload.access_token);
      setToken(payload.access_token);
      setUser(payload.user);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Authentication failed");
    }
  }

  async function submitReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("");
    const response = await fetch(`${API_BASE}/reviews`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(reviewForm),
    });

    if (!response.ok) {
      setNotice("Review submission failed.");
      return;
    }

    setReviewForm((current) => ({ ...current, comment: "" }));
    setNotice("Review submitted.");
    if (user) loadReviews(token, user.role);
  }

  async function submitMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = input.trim();
    if (!message || isLoading) return;

    setInput("");
    setIsLoading(true);
    setNotice("");
    setMessages((current) => [...current, { role: "user", content: message }]);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ message }),
      });
      if (!response.ok) throw new Error("Chat endpoint failed");
      const payload = await response.json();
      setMessages((current) => [
        ...current,
        { role: "assistant", content: payload.reply, tool: payload.tool_used },
      ]);
    } catch {
      setNotice("Admin AI request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("support-analyzer-token");
    setToken("");
    setUser(null);
    setReviews([]);
    setAnalysis(null);
    setPoints([]);
  }

  const traces = useMemo<Data[]>(() => {
    const labels = Array.from(new Set(points.map((point) => point.label)));
    return labels.map((label) => {
      const cluster = points.filter((point) => point.label === label);
      return {
        x: cluster.map((point) => point.x),
        y: cluster.map((point) => point.y),
        text: cluster.map(
          (point) =>
            `${point.id}<br>${point.title}<br>${point.text}<br>Severity: ${point.severity}<br>Channel: ${point.channel}`,
        ),
        name: label,
        type: "scatter",
        mode: "markers",
        marker: {
          color: palette[label] ?? "#475569",
          size: 11,
          opacity: 0.82,
          line: { color: "#ffffff", width: 1 },
        },
        hoverinfo: "text",
      };
    });
  }, [points]);

  const layout: Partial<Layout> = {
    autosize: true,
    margin: { l: 34, r: 18, t: 12, b: 34 },
    paper_bgcolor: "transparent",
    plot_bgcolor: "#f8fafc",
    font: { color: "#0f172a", family: "Inter, Arial, sans-serif" },
    legend: { orientation: "h", y: 1.12, x: 0 },
    xaxis: { title: { text: "PCA component 1" }, gridcolor: "#e2e8f0" },
    yaxis: { title: { text: "PCA component 2" }, gridcolor: "#e2e8f0" },
  };

  if (!user) {
    return (
      <AuthPanel
        authMode={authMode}
        authForm={authForm}
        notice={notice}
        setAuthMode={setAuthMode}
        setAuthForm={setAuthForm}
        submitAuth={submitAuth}
      />
    );
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <header className="border-b border-slate-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-slate-500">Customer Support Analyzer</p>
            <h1 className="text-xl font-semibold tracking-normal">
              {user.role === "admin" ? "Admin AI Dashboard" : "Customer Review Portal"}
            </h1>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="rounded-md bg-slate-100 px-3 py-2">
              {user.name} · {user.role}
            </span>
            <button className="rounded-md bg-slate-900 px-3 py-2 text-white" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      {notice && (
        <div className="mx-auto mt-4 max-w-7xl rounded-md border border-slate-200 bg-white px-4 py-2 text-sm">
          {notice}
        </div>
      )}

      {user.role === "admin" ? (
        <AdminDashboard
          analysis={analysis}
          reviews={reviews}
          messages={messages}
          input={input}
          isLoading={isLoading}
          setInput={setInput}
          submitMessage={submitMessage}
          plot={{ traces, layout, meta }}
        />
      ) : (
        <CustomerPortal
          reviewForm={reviewForm}
          setReviewForm={setReviewForm}
          submitReview={submitReview}
          reviews={reviews}
        />
      )}
    </main>
  );
}
