<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3>
        {{ title }}
        <ToggleQuestionMark :explanation="explanationText" />
      </h3>
    </div>
    <div class="chart-body">
      <div ref="plotlyContainer" class="chart-container"></div>
    </div>
  </div>
</template>

<script>
/**
 * HorizontalBoxPlotChart component
 *
 * Renders a horizontal boxplot chart using Chart.js and the @sgratzl/chartjs-chart-boxplot plugin.
 * Displays one or more boxplots horizontally, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <HorizontalBoxPlotChart
 * //   :data="boxplotData"
 * //   title="Horizontal Boxplot Example"
 * //   xAxisLabel="Values"
 * //   yAxisLabel="Categories"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the boxplot (required)
 * @prop {string} [title=''] - Title displayed above the chart
 * @prop {string} [xAxisLabel=''] - Label for the x-axis
 * @prop {string} [yAxisLabel=''] - Label for the y-axis
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 * - @sgratzl/chartjs-chart-boxplot
 *
 * @style
 * - Responsive chart area with fixed height.
 * - Container for the chart with relative positioning.
 */
import Plotly from "plotly.js-dist-min";
import { ref, onMounted, watch } from "vue";
import ToggleQuestionMark from "../Reusable/ToggleQuestionMark.vue";

export default {
  name: "BoxPlotChart",
  props: {
    title: {
      type: String,
      default: "Box Plot Chart",
    },
    xAxisLabel: {
      type: String,
      default: "X Axis",
    },
    yAxisLabel: {
      type: String,
      default: "Y Axis",
    },
    data: {
      type: Array,
      required: true,
      validator: (value) =>
        Array.isArray(value) && value.every((item) => typeof item === "number"),
    },
  },
  setup(props) {
    const plotlyContainer = ref(null);

    const calculateStatistics = (data) => {
      const sortedData = [...data].sort((a, b) => a - b);
      const n = sortedData.length;

      const q1Index = Math.floor(n * 0.25);
      const q2Index = Math.floor(n * 0.5);
      const q3Index = Math.floor(n * 0.75);

      const q1 = sortedData[q1Index];
      const median = sortedData[q2Index];
      const q3 = sortedData[q3Index];

      const iqr = q3 - q1;
      const lowerWhisker = Math.max(...sortedData.filter((x) => x >= q1 - 1.5 * iqr));
      const upperWhisker = Math.min(...sortedData.filter((x) => x <= q3 + 1.5 * iqr));

      const outliers = sortedData.filter((x) => x < lowerWhisker || x > upperWhisker);

      return {
        min: lowerWhisker,
        q1,
        median,
        q3,
        max: upperWhisker,
        outliers,
      };
    };

    const processData = (rawData) => {
      const stats = calculateStatistics(rawData);

      return [
        {
          type: "box",
          x: rawData,
          name: "",
          orientation: "h",
          boxmean: true,
          boxpoints: "suspectedoutliers",
          marker: {
            outliercolor: "rgba(255, 99, 132, 1)",
            color: "rgba(54, 162, 235, 0.5)",
          },
          line: {
            color: "rgba(54, 162, 235, 1)",
          },
        },
      ];
    };

    const renderPlot = () => {
      const plotData = processData(props.data);

      const layout = {
        xaxis: {
          title: {
            text: props.xAxisLabel,
            font: {
              family: "Arial, sans-serif",
              size: 14,
              color: "#555555",
              weight: "bold",
            },
          },
          gridcolor: "rgba(200, 200, 200, 0.2)", // Subtle grid lines
          zeroline: false,
        },
        yaxis: {
          title: {
            text: props.yAxisLabel,
            font: {
              family: "Arial, sans-serif",
              size: 14,
              color: "#555555",
              weight: "bold",
            },
          },
          gridcolor: "rgba(200, 200, 200, 0.2)", // Subtle grid lines
          zeroline: false,
        },
        showlegend: false,
        plot_bgcolor: "transparent",
        paper_bgcolor: "transparent",
        margin: { l: 50, r: 50, t: 50, b: 50 }, // Padding for cleaner layout
      };

      Plotly.newPlot(plotlyContainer.value, plotData, layout, { responsive: true });
    };

    onMounted(() => {
      renderPlot();
    });

    watch(
      () => props.data,
      () => {
        renderPlot();
      },
      { deep: true }
    );

    return {
      plotlyContainer,
    };
  },
};
</script>

<style scoped>
.chart-container {
  height: 250px;
  width: 100%;
  background-color: inherit;
}

.chart-card {
  background: #ffffff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 24px;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.chart-header h3 {
  margin: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: #222222;
}

.chart-body {
  position: relative;
  height: 300px;
}
</style>
