import type { Dispatch, FormEvent, SetStateAction } from "react";
import type { ChatMessage, Review } from "@/types";
import { ReviewList } from "./ReviewList";
import { ChatConsole } from "../admin/ChatConsole";

type ReviewForm = {
  rating: number;
  category: string;
  comment: string;
};

export function CustomerPortal({
  reviewForm,
  setReviewForm,
  submitReview,
  reviews,
  onDeleteReview,
  messages,
  input,
  isLoading,
  setInput,
  submitMessage,
}: {
  reviewForm: ReviewForm;
  setReviewForm: Dispatch<SetStateAction<ReviewForm>>;
  submitReview: (event: FormEvent<HTMLFormElement>) => void;
  reviews: Review[];
  onDeleteReview: (id: number) => void;
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  setInput: (value: string) => void;
  submitMessage: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="space-y-6">
        <ChatConsole
          messages={messages}
          input={input}
          isLoading={isLoading}
          setInput={setInput}
          submitMessage={submitMessage}
        />
        
        <form onSubmit={submitReview} className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold">Submit review</h2>
        <label className="mt-4 block text-sm font-medium">
          Rating
          <input
            className="mt-1 w-full"
            type="range"
            min="1"
            max="5"
            value={reviewForm.rating}
            onChange={(event) =>
              setReviewForm((current) => ({ ...current, rating: Number(event.target.value) }))
            }
          />
          <span className="text-sm text-slate-600">{reviewForm.rating} / 5</span>
        </label>
        <label className="mt-4 block text-sm font-medium">
          Category
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={reviewForm.category}
            onChange={(event) =>
              setReviewForm((current) => ({ ...current, category: event.target.value }))
            }
          >
            <option>Login</option>
            <option>Billing</option>
            <option>Performance</option>
            <option>Support Quality</option>
            <option>Feature Request</option>
          </select>
        </label>
        <label className="mt-4 block text-sm font-medium">
          Comment
          <textarea
            className="mt-1 min-h-36 w-full rounded-md border border-slate-300 px-3 py-2"
            value={reviewForm.comment}
            onChange={(event) =>
              setReviewForm((current) => ({ ...current, comment: event.target.value }))
            }
            required
            minLength={5}
          />
        </label>
        <button className="mt-4 rounded-md bg-slate-900 px-4 py-3 text-sm font-semibold text-white">
          Submit review
        </button>
        </form>
      </div>

    </div>
  );
}
