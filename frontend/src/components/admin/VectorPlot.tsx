"use client";

import dynamic from "next/dynamic";
import type { PlotConfig } from "@/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export function VectorPlot({ traces, layout, meta }: PlotConfig) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
        <div>
          <p className="text-sm font-medium text-slate-500">Admin-only visualization</p>
          <h2 className="text-xl font-semibold tracking-normal">PCA Ticket Clusters</h2>
        </div>
        <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
          {meta.embedding_dimensions}D to 2D
        </span>
      </header>
      <div className="min-h-0 p-3">
        <Plot
          data={traces}
          layout={layout}
          config={{ responsive: true, displaylogo: false }}
          className="h-full min-h-[620px] w-full"
          useResizeHandler
        />
      </div>
    </section>
  );
}
