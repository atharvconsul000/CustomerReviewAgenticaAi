import type { Review } from "@/types";

export function ReviewList({ 
  reviews, 
  title,
  isAdmin = false,
  onDelete,
  onRespond,
}: { 
  reviews: Review[]; 
  title: string;
  isAdmin?: boolean;
  onDelete?: (id: number) => void;
  onRespond?: (id: number, response: string) => void;
}) {
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
              
              {review.admin_response && (
                <div className="mt-3 rounded-md bg-blue-50 p-3 text-sm text-blue-900 border border-blue-100">
                  <span className="font-semibold block mb-1">Admin Response:</span>
                  {review.admin_response}
                </div>
              )}

              <div className="mt-3 flex gap-2">
                {onDelete && (
                  <button 
                    onClick={() => onDelete(review.id)}
                    className="text-xs text-red-600 hover:underline font-medium"
                  >
                    Delete
                  </button>
                )}
                {isAdmin && onRespond && (
                  <button
                    onClick={() => {
                      const response = prompt("Enter admin response:", review.admin_response || "");
                      if (response !== null) onRespond(review.id, response);
                    }}
                    className="text-xs text-blue-600 hover:underline font-medium"
                  >
                    {review.admin_response ? "Edit Response" : "Respond"}
                  </button>
                )}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
