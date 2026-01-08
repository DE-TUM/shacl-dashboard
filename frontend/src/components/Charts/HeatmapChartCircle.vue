<template>
    <div class="chart-card w-full">
      <div class="chart-header flex justify-between items-center">
        <h3 class="inline-flex items-center gap-2">
          {{ title }}
        </h3>
        <ToggleQuestionMark :explanation="explanationText" />
      </div>
  
      <div class="chart-body w-full" ref="chartContainer">
        <svg
          :width="responsiveWidth"
          :height="responsiveHeight"
          :viewBox="`0 0 ${responsiveWidth} ${responsiveHeight + margin.bottom}`"
        >
          <!-- Legend -->
          <g :transform="`translate(${margin.left}, 10)`">
            <defs>
              <linearGradient id="legend-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" :stop-color="getCellColor(0)" />
                <stop offset="100%" :stop-color="getCellColor(maxValue)" />
              </linearGradient>
            </defs>
  
            <rect
              :width="responsiveWidth - margin.left - margin.right"
              height="10"
              fill="url(#legend-gradient)"
              rx="2"
            />
  
            <text y="25" text-anchor="start" class="text-s font-medium" :fill="chartTheme.defaults.textColor">
              0
            </text>
            <text x="1310" y="25" text-anchor="end" class="text-s font-medium" :fill="chartTheme.defaults.textColor">
              {{ maxValue }}
            </text>
            <text x="707" y="25" text-anchor="middle" class="text-s font-medium" :fill="chartTheme.defaults.textColor">
              Number of Violations
            </text>
          </g>
  
          <!-- Main chart -->
          <g :transform="`translate(0, ${margin.top - 40})`">
            <!-- Y-axis labels -->
            <svg :width="responsiveWidth" :height="responsiveHeight">
            <!-- Y-axis interactive circles -->
            <g>
            <circle
              v-for="(prop, i) in processedData.properties"
              :key="`y-circle-${i}`"
              :cx="margin.left - 10"
              :cy="margin.top + (i + 0.5) * cellHeight"
              r="5"
              fill="blue"
              @mouseenter="(event) => showTooltip(prop, event)"
              @mouseleave="hideTooltip"
              style="cursor: pointer;"
            />
          </g>
  
            <!-- X-axis interactive circles -->
            <g>
              <circle
                v-for="(constraint, i) in processedData.constraints"
                :key="`x-circle-${i}`"
                :cx="margin.left + (i + 0.5) * cellWidth"
                :cy="responsiveHeight - margin.bottom + 20"
                r="5"
                fill="blue"
                @mouseenter="(event) => showTooltip(constraint, event)"
                @mouseleave="hideTooltip"
                style="cursor: pointer;"
              />
            </g>
          </svg>
  
            <!-- Axis titles -->
            <g>
              <text
                :x="responsiveWidth / 2"
                :y="responsiveHeight - margin.bottom + 55"
                text-anchor="middle"
                class="font-medium text-sm responsive-text"
                :fill="chartTheme.defaults.textColor"
              >
                Constraint Components
              </text>
  
              <text
                :x="-responsiveHeight / 2 + 10"
                :y="25"
                text-anchor="middle"
                transform="rotate(-90)"
                class="font-medium text-sm responsive-text"
                :fill="chartTheme.defaults.textColor"
              >
                Property Shapes
              </text>
            </g>
  
            <!-- Grid and heatmap cells -->
            <g :transform="`translate(${margin.left}, ${margin.top})`">
              <!-- Grid lines -->
              <g>
                <line
                  v-for="(_, i) in processedData.properties"
                  :key="`h-${i}`"
                  :x1="0"
                  :y1="i * cellHeight"
                  :x2="innerWidth"
                  :y2="i * cellHeight"
                  :stroke="chartTheme.defaults.gridlineColor"
                  stroke-width="1"
                />
                <line
                  v-for="(_, i) in processedData.constraints"
                  :key="`v-${i}`"
                  :x1="i * cellWidth"
                  :y1="0"
                  :x2="i * cellWidth"
                  :y2="innerHeight"
                  :stroke="chartTheme.defaults.gridlineColor"
                  stroke-width="1"
                />
              </g>
  
              <!-- Heatmap cells -->
              <g>
                <template v-for="(row, i) in processedData.violations" :key="`row-${i}`">
                  <template v-for="(value, j) in row" :key="`cell-${i}-${j}`">
                    <g 
                      @mouseenter="showTooltip(i, j, $event)" 
                      @mouseleave="hideTooltip"
                      class="cell-group"
                    >
                      <rect
                        :x="j * cellWidth"
                        :y="i * cellHeight"
                        :width="cellWidth"
                        :height="cellHeight"
                        :fill="getCellColor(value)"
                        stroke="#fff"
                        stroke-width="1"
                        class="cell-hover"
                      />
                      <text
                        v-if="value > 0"
                        :x="j * cellWidth + cellWidth / 2"
                        :y="i * cellHeight + cellHeight / 2"
                        text-anchor="middle"
                        dominant-baseline="middle"
                        :fill="value / maxValue > 0.5 ? '#fff' : '#000'"
                        class="text-xs font-medium responsive-text"
                      >
                        {{ value }}
                      </text>
                    </g>
                  </template>
                </template>
              </g>
            </g>
          </g>
        </svg>
        <!-- Tooltip (Move it outside the SVG to avoid rendering issues) -->
        <div
          v-if="tooltipVisible"
          class="custom-tooltip"
          :style="tooltipStyle"
        >
          {{ tooltipContent }}
        </div>
      </div>
    </div>
  </template>
  
  
  <script setup>
/**
 * HeatmapChartCircle component
 *
 * Renders a circular heatmap chart using Chart.js.
 * Displays data as colored segments in a circular layout, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <HeatmapChartCircle
 * //   :data="circleHeatmapData"
 * //   title="Circular Heatmap Example"
 * //   xAxisLabel="X Axis"
 * //   yAxisLabel="Y Axis"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the circular heatmap (required)
 * @prop {string} [title=''] - Title displayed above the chart
 * @prop {string} [xAxisLabel=''] - Label for the x-axis
 * @prop {string} [yAxisLabel=''] - Label for the y-axis
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 * - chartjs-chart-matrix or a circular heatmap plugin (if required)
 *
 * @style
 * - Responsive chart area with fixed height.
 * - Container for the chart with relative positioning.
 */
  import { computed, ref , onMounted, onUnmounted} from "vue";
  import { chartTheme } from "./../../assets/chartTheme";
  import ToggleQuestionMark from "../Reusable/ToggleQuestionMark.vue";
  import * as d3 from "d3-scale";
  
  const props = defineProps({
    title: { type: String, default: "Violation Heatmap" },
    data: { type: Array, required: true },
  });
  
  // Ensure margin is defined before being used
  const margin = {
    top: 40,
    right: 0,
    bottom: 30,
    left: 80,
  };
  
  const chartContainer = ref(null);
  const responsiveWidth = ref(3000);
  const responsiveHeight = ref(350);
  
  // Observing container size to make it responsive
  const resizeObserver = new ResizeObserver((entries) => {
    for (let entry of entries) {
      responsiveWidth.value = entry.contentRect.width;
      responsiveHeight.value = entry.contentRect.height;
    }
  });
  
  // Attach observer on mount
  onMounted(() => {
    if (chartContainer.value) {
      resizeObserver.observe(chartContainer.value);
    }
  });
  
  // Clean up observer on unmount
  onUnmounted(() => {
    if (chartContainer.value) {
      resizeObserver.unobserve(chartContainer.value);
    }
  });
  
  
  const baseWidth = 1800;
  const baseHeight = 350;
  
  // Computed responsive width and height
  const innerWidth = computed(() => responsiveWidth.value - margin.left - margin.right);
  const innerHeight = computed(() => responsiveHeight.value - margin.top - margin.bottom);
  // Compute cell sizes based on chart dimensions
  const cellWidth = computed(() => {
    return processedData.value.constraints.length > 0
      ? innerWidth.value / processedData.value.constraints.length
      : 0;
  });
  
  const cellHeight = computed(() => {
    return processedData.value.properties.length > 0
      ? innerHeight.value / processedData.value.properties.length
      : 0;
  });
  
  const tooltipVisible = ref(false);
  const tooltipContent = ref("");
  const tooltipStyle = ref({});
  
  const showTooltip = (text, event) => {
    if (!event || !event.clientX || !event.clientY) return;
  
    tooltipContent.value = text;
    tooltipVisible.value = true;
  
    tooltipStyle.value = {
      left: `${event.clientX + 10}px`,
      top: `${event.clientY + 10}px`,
      position: "fixed",
      transform: "translate(-50%, -100%)",
      zIndex: 1000, // Ensures the tooltip is on top
    };
  };
  
  const hideTooltip = () => {
    tooltipVisible.value = false;
  };
  
  // Process the data dynamically
  const processedData = computed(() => {
    if (!props.data) {
      return { properties: [], constraints: [], violations: [] };
    }
  
    // Ensure props.data is always an array
    const inputData = Array.isArray(props.data) ? props.data : [props.data];
  
    const propertiesSet = new Set();
    const constraintsSet = new Set();
  
    inputData.forEach((entry) => {
      if (!entry.PropertyShape || !entry.Constraints) return;
      
      propertiesSet.add(entry.PropertyShape);
      entry.Constraints.forEach((constraint) => {
        if (constraint.Constraint) constraintsSet.add(constraint.Constraint);
      });
    });
  
    const properties = Array.from(propertiesSet);
    const constraints = Array.from(constraintsSet);
  
    const violationsMatrix = Array.from({ length: properties.length }, () =>
      Array(constraints.length).fill(0)
    );
  
    inputData.forEach((entry) => {
      const propIndex = properties.indexOf(entry.PropertyShape);
      entry.Constraints.forEach((constraint) => {
        if (constraint.Constraint) {
          const constraintIndex = constraints.indexOf(constraint.Constraint);
          violationsMatrix[propIndex][constraintIndex] = constraint.Violations;
        }
      });
    });
  
    return { properties, constraints, violations: violationsMatrix };
  });
  
  const maxValue = computed(() => {
    if (processedData.value.violations.length === 0) return 1; // Avoid division by zero
    return Math.max(...processedData.value.violations.flat());
  });
  
  const quantileScale = d3.scaleQuantile()
    .domain([18, 27, 93, 2214]) // Your actual values
    .range(["hsl(211, 95%, 85%)", "hsl(211, 95%, 70%)", "hsl(211, 95%, 55%)", "hsl(211, 95%, 40%)"]);
  
  const getCellColor = (value) => {
    if (value === 0) return chartTheme.colors.neutral;
    return quantileScale(value);
  };
  
  </script>
  
  <style scoped>
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
    /* transform: translateY(-2px); */
  }
  
  .chart-header h3 {
    margin: 0 0 8px;
    font-size: 18px;
    font-weight: 600;
    color: #222222;
    line-height: 1.2;
  }
  
  .chart-body {
    position: relative;
    height: 300px; /* Adjusted to fit content */
    width: 100%;
    margin: 0 auto;
  }
  
  .cell-hover {
    transition: opacity 0.2s ease;
    cursor: pointer;
  }
  
  .cell-group:hover .cell-hover {
    opacity: 0.8;
  }
  
  .custom-tooltip {
    position: fixed;
    z-index: 1000;
    background-color: rgba(17, 24, 39, 0.95);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    pointer-events: none;
    white-space: nowrap;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: opacity 0.15s ease;
  }
  
  text {
    user-select: none;
  }
  
  .responsive-text {
    font-size: 0.75rem; /* Decreases font size on smaller screens */
  }
  
  @media (min-width: 600px) {
    .responsive-text {
      font-size: 1rem; /* Default size for larger screens */
    }
  }
  </style>
