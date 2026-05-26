import type { Dispatch, FormEvent, SetStateAction } from "react";
import type { Review } from "@/types";
import { ReviewList } from "./ReviewList";

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
}: {
  reviewForm: ReviewForm;
  setReviewForm: Dispatch<SetStateAction<ReviewForm>>;
  submitReview: (event: FormEvent<HTMLFormElement>) => void;
  reviews: Review[];
}) {
  return (
    <div className="mx-auto grid max-w-7xl gap-4 px-4 py-4 lg:grid-cols-[0.8fr_1.2fr]">
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
          />
        </label>
        <button className="mt-4 rounded-md bg-slate-900 px-4 py-3 text-sm font-semibold text-white">
          Submit review
        </button>
      </form>

      <ReviewList reviews={reviews} title="My reviews" />
    </div>
  );
}
