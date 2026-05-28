import { FormEvent, useState } from "react";
import type { Analysis, ChatMessage, PlotConfig, Review } from "@/types";
import { Metric } from "@/components/common/Metric";
import { ReviewList } from "@/components/reviews/ReviewList";
import { ChatConsole } from "./ChatConsole";
import { VectorPlot } from "./VectorPlot";

export function AdminDashboard({
  analysis,
  reviews,
  messages,
  input,
  isLoading,
  setInput,
  submitMessage,
  plot,
  onDeleteReview,
  onRespondReview,
}: {
  analysis: Analysis | null;
  reviews: Review[];
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  setInput: (value: string) => void;
  submitMessage: (event: FormEvent<HTMLFormElement>) => void;
  plot: PlotConfig;
  onDeleteReview: (id: number) => void;
  onRespondReview: (id: number, response: string) => void;
}) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredReviews = reviews.filter((review) => {
    const q = searchQuery.toLowerCase();
    return (
      review.category.toLowerCase().includes(q) ||
      review.comment.toLowerCase().includes(q) ||
      (review.admin_response?.toLowerCase().includes(q) ?? false) ||
      (review.user_name?.toLowerCase().includes(q) ?? false)
    );
  });

  return (
    <div className="mx-auto grid max-w-7xl gap-4 px-4 py-4 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-3">
          <Metric label="Reviews" value={analysis?.total_reviews ?? 0} />
          <Metric label="Average rating" value={analysis?.average_rating ?? 0} />
          <Metric label="Vector tickets" value={plot.meta.tickets} />
        </div>

        <ChatConsole
          messages={messages}
          input={input}
          isLoading={isLoading}
          setInput={setInput}
          submitMessage={submitMessage}
        />

        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <input
            type="text"
            placeholder="Search reviews by name, category, or comment..."
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <ReviewList 
          reviews={filteredReviews} 
          title="All customer reviews" 
          isAdmin={true}
          onDelete={onDeleteReview}
          onRespond={onRespondReview}
        />
      </section>

      <VectorPlot {...plot} />
    </div>
  );
}
