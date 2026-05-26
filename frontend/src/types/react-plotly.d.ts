declare module "react-plotly.js" {
  import type { ComponentType } from "react";
  import type { Config, Data, Layout } from "plotly.js";

  type PlotProps = {
    data: Data[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    className?: string;
    useResizeHandler?: boolean;
  };

  const Plot: ComponentType<PlotProps>;
  export default Plot;
}
