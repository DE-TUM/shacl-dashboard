# SHACL Dashboard Frontend

This is the frontend application for the SHACL Dashboard, built with [Vue 3](https://vuejs.org/) and [Vite](https://vitejs.dev/). It provides an interactive web interface for visualizing and analyzing SHACL validation results.

## Features

- Modern Vue 3 SPA with [Vuetify](https://vuetifyjs.com/) for UI components
- Data visualizations using Chart.js and D3.js
- Responsive layout with Tailwind CSS utility classes
- Routing with Vue Router
- Modular component structure
- CSV export and filtering for validation results

## Project Structure

```
frontend/
  ├── public/           # Static assets (images, reports, etc.)
  ├── src/
  │   ├── assets/       # CSS, chart themes, and static resources
  │   ├── components/   # Vue components (charts, tables, layout, etc.)
  │   ├── router/       # Vue Router configuration
  │   ├── utils/        # Utility functions
  │   └── main.js       # App entry point
  ├── index.html        # Main HTML file
  ├── package.json      # NPM dependencies and scripts
  ├── tailwind.config.js
  ├── postcss.config.js
  └── vite.config.js
```

## Detailed Structure of the `src` Folder

```
src/
├── App.vue                        # Root Vue component, sets up the app shell and main layout
├── main.js                        # App entry point, initializes Vue, plugins, and mounts the app
├── assets/
│   ├── base.css                   # CSS variables and color palette for consistent theming
│   ├── chartTheme.js              # Chart.js/D3.js color and style configuration for all charts
│   ├── logo.svg                   # Project logo (SVG format) for branding
│   └── main.css                   # Main CSS file, imports base.css and Tailwind for global styles
├── components/
│   ├── LandingPage.vue            # Entry page for user input, file upload, and dashboard start
│   ├── Charts/
│   │   ├── BarChart.vue                   # Bar chart for violations and metrics
│   │   ├── BoxPlot.vue                    # Box plot for distribution analysis
│   │   ├── BubbleChart.vue                # Bubble chart for multi-variate data
│   │   ├── ConstraintAnalysisChart.vue    # Specialized chart for constraint analysis
│   │   ├── GaugeChart.vue                 # Gauge for health/score metrics
│   │   ├── GroupedBarChart.vue            # Grouped bar chart for comparative stats
│   │   ├── HeatmapChart.vue               # Heatmap for visualizing matrix data
│   │   ├── HeatmapChartCircle.vue         # Circular heatmap variant for advanced visualizations
│   │   ├── HistogramChart.vue             # Histogram for frequency distributions
│   │   ├── HorizontalBoxPlotChart.vue     # Horizontal box plot for distributions
│   │   ├── NodeShapeOverlapChart.vue      # Visualizes overlap between node shapes and constraints
│   │   ├── ParetoChart.vue                # Pareto chart for identifying major contributors
│   │   ├── RadarChart.vue                 # Radar chart for multi-metric comparison
│   │   ├── ScatterPlotChart.vue           # Scatter plot for property shape analysis
│   │   ├── ShannonScatterPlotChart.vue    # Scatter plot with quadrant analysis for diversity/intensity
│   │   ├── SparklineChart.vue             # Small inline charts for metric cards
│   │   ├── StackedBarChart.vue            # Stacked bar chart for grouped data
│   │   └── ViolationExamplesChart.vue     # Chart for visualizing example violations
│   ├── ConstraintView/
│   │   └── Metrics.vue                    # Key metrics for a constraint view (cards with stats)
│   ├── FocusNodeView/
│   │   └── Metrics.vue                    # Key metrics for a focus node view (cards with stats)
│   ├── icons/
│   │   ├── IconCommunity.vue              # Community SVG icon for About/Team sections
│   │   ├── IconDocumentation.vue          # Documentation SVG icon
│   │   ├── IconEcosystem.vue              # Ecosystem SVG icon
│   │   ├── IconSupport.vue                # Support SVG icon
│   │   └── IconTooling.vue                # Tooling SVG icon
│   ├── Layout/
│   │   ├── MainContent.vue                # Main dashboard content: stats, charts, tables
│   │   ├── MainLayout.vue                 # Top-level layout: navigation, sidebar, router-view
│   │   ├── Navigation.vue                 # Top navigation bar with links and user controls
│   │   └── SideBar.vue                    # Sidebar navigation for dashboard sections
│   ├── Overviews/
│   │   ├── AboutUs.vue                    # About/team information page
│   │   ├── ConstraintOverview.vue         # Overview of all constraints and their usage/violations
│   │   ├── FocusNodeOverview.vue          # Overview of focus nodes and their stats
│   │   ├── PropertyPathOverview.vue       # Overview of property paths and related metrics
│   │   └── ShapeOverview.vue              # Overview of all node shapes and their stats
│   ├── PropertyPathView/                        
│   │   └── Metrics.vue                    # Key metrics for a PropertyPath view (cards with stats)
│   ├── Reusable/
│   │   ├── ConfirmationModal.vue          # Modal dialog for confirmations (e.g., delete, reset)
│   │   ├── DropDownMenu.vue               # Dropdown menu for filters and selections
│   │   ├── ExternalLink.vue               # External link component with icon
│   │   ├── Filter.vue                     # Multi-dropdown filtering interface for tables/lists
│   │   ├── PersonCard.vue                 # Card for displaying a person's info (About/Team)
│   │   ├── Search.vue                     # Search input component for tables/lists
│   │   ├── SearchAndFilter.vue            # Combined search and filter interface
│   │   ├── ShapesTable.vue                # Table for listing property shapes and stats
│   │   ├── ShapesTablePropertyShape.vue   # Expandable row for property shape details
│   │   ├── Tag.vue                        # Tag/badge component for labels and highlights
│   │   ├── ToggleQuestionMark.vue         # Toggleable question mark/help icon
│   │   ├── ViolationTable.vue             # Table for listing violations
│   │   └── ViolationTableRow.vue          # Expandable row for violation details
│   ├── ShapeView/
│   │   └── Metrics.vue                    # Key metrics for a shape view (cards with stats)
│   └── Views/
│       ├── ConstraintView.vue             # Main view for a single constraint (dashboard, charts, table)
│       ├── FocusNodeView.vue              # Main view for a single focus node (dashboard, charts, table)
│       ├── PropertyPathView.vue           # Main view for a single property path (dashboard, charts, table)
│       └── ShapeView.vue                  # Main view for a single shape, with charts and tables
├── router/
│   └── index.js                   # Vue Router configuration and route definitions
└── utils/
    └── utils.js                   # Utility functions for data parsing, formatting, etc.
```

### Folder and File Descriptions

- **App.vue**: Root Vue component, sets up the app shell and main layout.
- **main.js**: App entry point, initializes Vue, Vuetify, FontAwesome, router, and mounts the app.

#### assets/
- **base.css**: CSS variables and color palette for consistent theming.
- **main.css**: Imports base.css and Tailwind, sets global styles.
- **chartTheme.js**: Defines color schemes and chart appearance for all charts, using CSS variables.
- **logo.svg**: Project logo used in the header and landing page.

#### components/
- **LandingPage.vue**: Landing page for user input (directory, shapes graph, validation report).
- **Charts/**: All chart and visualization components for dashboards and overviews.
  - `BarChart.vue`, `BoxPlot.vue`, `BubbleChart.vue`, `ConstraintAnalysisChart.vue`, `GaugeChart.vue`, `GroupedBarChart.vue`, `HeatmapChart.vue`, `HeatmapChartCircle.vue`, `HistogramChart.vue`, `HorizontalBoxPlotChart.vue`, `NodeShapeOverlapChart.vue`, `ParetoChart.vue`, `RadarChart.vue`, `ScatterPlotChart.vue`, `ShannonScatterPlotChart.vue`, `SparklineChart.vue`, `StackedBarChart.vue`, `ViolationExamplesChart.vue`: Specialized chart components for various data visualizations.
- **ConstraintView/**: Components for displaying detailed information about constraints (e.g., `Metrics.vue` for constraint metrics).
- **FocusNodeView/**: Components for focus node-specific validation results (e.g., `Metrics.vue` for focus node metrics).
- **icons/**: SVG icon components (e.g., `IconDocumentation.vue`, `IconEcosystem.vue`, `IconCommunity.vue`, `IconSupport.vue`, `IconTooling.vue`).
- **Layout/**: Layout components for the main dashboard (e.g., `MainContent.vue` for dashboard content, `MainLayout.vue` for top-level layout, `Navigation.vue` for the top navigation bar, `SideBar.vue` for sidebar navigation).
- **Overviews/**: High-level overview pages for shapes, constraints, property paths, focus nodes, and team info.
  - `AboutUs.vue`: About/team information page.
  - `ConstraintOverview.vue`: Overview of all constraints and their usage/violations.
  - `FocusNodeOverview.vue`: Overview of focus nodes and their stats.
  - `PropertyPathOverview.vue`: Overview of property paths and related metrics.
  - `ShapeOverview.vue`: Overview of all node shapes and their stats.
- **PropertyPathView/**: Components for detailed property path analysis (e.g., `Metrics.vue` for property path metrics).
- **Reusable/**: Generic, reusable UI components, especially tables, dropdowns, modals, and expandable rows for displaying shape and violation details.
  - `ConfirmationModal.vue`: Modal dialog for confirmations.
  - `DropDownMenu.vue`: Dropdown menu for filters and selections.
  - `ExternalLink.vue`: External link component with icon.
  - `Filter.vue`: Multi-dropdown filtering interface for tables/lists.
  - `PersonCard.vue`: Card for displaying a person's info (About/Team).
  - `Search.vue`: Search input component for tables/lists.
  - `SearchAndFilter.vue`: Combined search and filter interface.
  - `ShapesTable.vue`: Table for listing property shapes and stats.
  - `ShapesTablePropertyShape.vue`: Expandable row for property shape details.
  - `Tag.vue`: Tag/badge component for labels and highlights.
  - `ToggleQuestionMark.vue`: Toggleable question mark/help icon.
  - `ViolationTable.vue`: Table for listing violations.
  - `ViolationTableRow.vue`: Expandable row for violation details.
- **ShapeView/**: Components for detailed node shape views (e.g., `Metrics.vue` for shape metrics).
- **Views/**: Main routed views for the application.
  - `ConstraintView.vue`: Main view for a single constraint (dashboard, charts, table).
  - `FocusNodeView.vue`: Main view for a single focus node (dashboard, charts, table).
  - `PropertyPathView.vue`: Main view for a single property path (dashboard, charts, table).
  - `ShapeView.vue`: Main view for a single shape, with charts and tables.

#### router/
- **index.js**: Vue Router configuration and route definitions for landing page, dashboard, about, and all main views.

#### utils/
- **utils.js**: Utility functions for data parsing, formatting, and helpers used across components.

---

**Descriptions:**

- **assets/**
  - `chartTheme.js`: Sets up color palettes and chart appearance for all charts.
  - `logo.svg`: Logo image for branding.
  - `main.css`, `base.css`: Custom CSS for global styles and color variables.

- **components/**
  - `LandingPage.vue`: Landing page for user input and configuration.
  - `Charts/`: All chart and visualization components for dashboards and overviews.
  - `ConstraintView/`, `FocusNodeView/`, `PropertyPathView/`, `ShapeView/`: Metrics and detail components for each entity type.
  - `icons/`: SVG icon components for UI and documentation.
  - `Layout/`: Main layout, navigation, and sidebar components.
  - `Overviews/`: Overview pages for shapes, constraints, property paths, focus nodes, and team info.
  - `Reusable/`: Generic, reusable UI components (tables, modals, filters, etc.).
  - `Views/`: Main routed views for each dashboard section.

- **router/**
  - `index.js`: Sets up all application routes and navigation.

- **utils/**
  - `utils.js`: Utility functions for data parsing, formatting, and helpers.

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or newer recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)

### Installation

1. **Install dependencies:**

   ```sh
   npm install
   ```

2. **Run the development server:**

   ```sh
   npm run dev
   ```

   The app will be available at [http://localhost:5173](http://localhost:5173) by default.

### Building for Production

To build the frontend for production (output in `dist/`):

```sh
npm run build
```

To preview the production build locally:

```sh
npm run preview
```

### Linting and Formatting

- **Lint code with ESLint:**

  ```sh
  npm run lint
  ```

- **Format code with Prettier:**

  ```sh
  npm run format
  ```

## Customization

- **Tailwind CSS**: UI classes are configured in [`tailwind.config.js`](tailwind.config.js).
- **Vuetify**: UI components and theming.
- **Chart Themes**: See [`src/assets/chartTheme.js`](src/assets/chartTheme.js) for chart color and style configuration.
- **Static Reports**: Place example or result JSON/TTL files in [`public/reports/`](public/reports/).

## Directory Overview

- **Landing Page**: User inputs for Virtuoso directory, shapes graph, and validation report.
- **Main Dashboard**: Visualizes SHACL validation results with charts and tables.
- **About Us**: Team and project information.
- **Reusable Components**: Modular charts, tables, and UI elements.

## Development Notes

- Uses [Vite](https://vitejs.dev/) for fast development and hot module replacement.
- [Vue Router](src/router/index.js) manages navigation between dashboard views.
- [Vuetify](https://vuetifyjs.com/) and [Tailwind CSS](https://tailwindcss.com/) are both used for styling.
- Data visualizations use Chart.js, D3.js, and custom themes.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.

---

For more details, see the main [README.md](../README.md) in the project root.
