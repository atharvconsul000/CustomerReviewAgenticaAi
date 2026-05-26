import type { FormEvent } from "react";
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
}: {
  analysis: Analysis | null;
  reviews: Review[];
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  setInput: (value: string) => void;
  submitMessage: (event: FormEvent<HTMLFormElement>) => void;
  plot: PlotConfig;
}) {
  return (
    <div className="mx-auto grid max-w-7xl gap-4 px-4 py-4 xl:grid-cols-[0.9fr_1.1fr]">
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

        <ReviewList reviews={reviews} title="All customer reviews" />
      </section>

      <VectorPlot {...plot} />
    </div>
  );
}
