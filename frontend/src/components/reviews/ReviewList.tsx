import type { Review } from "@/types";

export function ReviewList({ reviews, title }: { reviews: Review[]; title: string }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <header className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-lg font-semibold">{title}</h2>
      </header>
      <div className="divide-y divide-slate-200">
        {reviews.length === 0 ? (
          <p className="p-5 text-sm text-slate-500">No reviews yet.</p>
        ) : (
          reviews.map((review) => (
            <article key={review.id} className="p-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="font-semibold">{review.category}</p>
                  {review.user_email && (
                    <p className="text-xs text-slate-500">
                      {review.user_name} · {review.user_email}
                    </p>
                  )}
                </div>
                <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium">
                  {review.rating} / 5 · {review.status}
                </span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-700">{review.comment}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
