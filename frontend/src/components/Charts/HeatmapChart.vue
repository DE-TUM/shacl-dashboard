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
        :viewBox="`0 0 ${baseWidth} ${baseHeight + margin.bottom}`" 
      >
        <!-- Legend (positioned higher) -->
        <g :transform="`translate(${margin.left}, 10)`">
          <defs>
            <linearGradient id="legend-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" :stop-color="getCellColor(0)" />
              <stop offset="100%" :stop-color="getCellColor(maxValue)" />
            </linearGradient>
          </defs>

          <rect
            :width="baseWidth - margin.left - margin.right"
            height="10"
            fill="url(#legend-gradient)"
            rx="2"
          />

          <text
            y="25"
            text-anchor="start"
            class="text-xs"
            :fill="chartTheme.defaults.textColor"
          >
            0
          </text>
          <text
            x="600"
            y="25"
            text-anchor="end"
            class="text-xs"
            :fill="chartTheme.defaults.textColor"
          >
            {{ maxValue }}
          </text>
          <text
            x="300"
            y="25"
            text-anchor="middle"
            class="text-xs font-medium"
            :fill="chartTheme.defaults.textColor"
          >
            Number of Violations
          </text>
        </g>

        <!-- Main chart group moved up -->
        <g :transform="`translate(0, ${margin.top - 40})`"> 
          <!-- Y-axis labels -->
          <g>
            <text
              v-for="(prop, i) in data.properties"
              :key="`y-${i}`"
              :x="margin.left - 10"
              :y="margin.top + (i + 0.5) * cellHeight"
              text-anchor="end"
              dominant-baseline="middle"
              class="text-sm responsive-text"
              :fill="chartTheme.defaults.textColor"
            >
              {{ prop }}
            </text>
          </g>

          <!-- X-axis labels positioned higher -->
          <g>
            <text
              v-for="(constraint, i) in data.constraints"
              :key="`x-${i}`"
              :x="margin.left + (i + 0.5) * cellWidth"
              :y="baseHeight - margin.bottom + 20" 
              text-anchor="middle"
              class="text-sm responsive-text"
              :fill="chartTheme.defaults.textColor"
            >
              {{ constraint }}
            </text>
          </g>

          <!-- Axis titles positioned higher -->
          <g>
            <text
              :x="baseWidth / 2"
              :y="baseHeight - margin.bottom + 55"
              text-anchor="middle"
              class="font-medium text-sm responsive-text"
              :fill="chartTheme.defaults.textColor"
            >
              Constraint Components 
            </text>
            
            <text
              :x="-baseHeight / 2 + 10"
              :y="25"
              text-anchor="middle"
              transform="rotate(-90)"
              class="font-medium text-sm responsive-text"
              :fill="chartTheme.defaults.textColor"
            >
              Property Shapes
            </text>
          </g>

          <!-- Grid and cells -->
          <g :transform="`translate(${margin.left}, ${margin.top})`">
            <!-- Grid lines -->
            <g>
              <line
                v-for="(_, i) in data.properties"
                :key="`h-${i}`"
                :x1="0"
                :y1="i * cellHeight"
                :x2="innerWidth"
                :y2="i * cellHeight"
                :stroke="chartTheme.defaults.gridlineColor"
                stroke-width="1"
              />
              <line
                v-for="(_, i) in data.constraints"
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
              <template v-for="(row, i) in data.violations" :key="`row-${i}`">
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
    </div>

    <div
      v-show="tooltipVisible"
      class="custom-tooltip"
      :style="tooltipStyle"
    >
      {{ tooltipContent }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { chartTheme } from './../../assets/chartTheme';
import ToggleQuestionMark from "../Reusable/ToggleQuestionMark.vue";

const props = defineProps({
  title: {
    type: String,
    default: 'Violation Heatmap',
  },
  data: {
    type: Object,
    default: () => ({
      properties: ['Property Shape 1', 'Property Shape 2', 'Property Shape 3'],
      constraints: ['sh:minCount', 'sh:maxCount', 'sh:datatype'],
      violations: [
        [3, 0, 0],
        [0, 2, 0],
        [0, 0, 1],
      ],
    }),
  },
});

const margin = {
  top: 40,    // Reduced from 50
  right: 40,
  bottom: 40, // Increased to create more space below
  left: 200,
};

const baseWidth = 1800;
const baseHeight = 350; // Slightly increased height

// Responsive setup
const chartContainer = ref(null);
const responsiveWidth = ref(baseWidth);
const responsiveHeight = ref(baseHeight);

// Computed dimensions
const innerWidth = computed(() => baseWidth - margin.left - margin.right);
const innerHeight = computed(() => baseHeight - margin.top - margin.bottom);
const cellWidth = computed(() => innerWidth.value / props.data.constraints.length);
const cellHeight = computed(() => innerHeight.value / props.data.properties.length);
const maxValue = computed(() => Math.max(...props.data.violations.flat()));

// Color scaling
const getCellColor = (value) => {
  if (value === 0) return chartTheme.colors.neutral;
  const intensity = (value / maxValue.value) * 100;
  return `hsl(211, 95%, ${80 - intensity * 0.4}%)`;
};

// Tooltip logic
const tooltipVisible = ref(false);
const tooltipContent = ref('');
const tooltipStyle = ref({});

const showTooltip = (i, j, event) => {
  tooltipContent.value = `${props.data.properties[i]}: ${props.data.violations[i][j]} violations for ${props.data.constraints[j]}`;
  tooltipVisible.value = true;

  // Use the event position instead of manually computing the heatmap's box position
  const mouseX = event.clientX; // Mouse X position in viewport
  const mouseY = event.clientY; // Mouse Y position in viewport

  tooltipStyle.value = {
    left: `${mouseX + 10}px`, // Position tooltip slightly to the right of the cursor
    top: `${mouseY}px`,  // Align with cursor's Y position
    transform: 'translate(0, -50%)', // Adjust tooltip so it aligns correctly with row
  };
};
const hideTooltip = () => {
  tooltipVisible.value = false;
};

// Resize handling using ResizeObserver
const resizeObserver = ref(null);
const handleResize = () => {
  const containerWidth = chartContainer.value.clientWidth;
  const containerHeight = baseHeight; // Fixed height for the chart component
  
  responsiveWidth.value = containerWidth;
  responsiveHeight.value = containerHeight;
};

onMounted(() => {
  resizeObserver.value = new ResizeObserver(handleResize);
  resizeObserver.value.observe(chartContainer.value);
});

onUnmounted(() => {
  if (resizeObserver.value) {
    resizeObserver.value.disconnect();
  }
});
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
  z-index: 50;
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
