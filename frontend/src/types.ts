import type { Data, Layout } from "plotly.js";

export type User = {
  id: number;
  name: string;
  email: string;
  role: "user" | "admin";
};

export type Review = {
  id: number;
  rating: number;
  category: string;
  comment: string;
  status: string;
  created_at: string;
  user_name?: string;
  user_email?: string;
};

export type Analysis = {
  total_reviews: number;
  average_rating: number;
  categories: { category: string; count: number; average_rating: number }[];
  statuses: { status: string; count: number }[];
};

export type PlotPoint = {
  id: string;
  x: number;
  y: number;
  label: string;
  title: string;
  text: string;
  severity: string;
  channel: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  tool?: string;
};

export type PlotConfig = {
  traces: Data[];
  layout: Partial<Layout>;
  meta: { tickets: number; embedding_dimensions: number };
};
