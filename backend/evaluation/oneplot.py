import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch

# Use seaborn style
sns.set_theme(style="whitegrid")
script_dir = os.getcwd()

# Custom dataset colors (from seaborn-muted palette, slightly adjusted)
custom_dataset_colors = {
    "DB100": "#9467bd",
    "DB1000": "#1f77b4",
    "DB50": "#d62728",
    "InvDa": "#8c564b",
    "LKG3": "#ff7f0e",
    "MKG3": "#2ca02c",
    "SKG3": "#17becf",
}

custom_order = ["SKG3", "MKG3", "LKG3", "DB50", "DB100", "DB1000", "InvDa"]

# Simulated bold title using LaTeX mathtext
legend_title_patch = Patch(facecolor='none', edgecolor='none', label=r'$\bf{Datasets:}$')

legend_handles = [legend_title_patch] + [
    Patch(facecolor=custom_dataset_colors[ds], label=ds)
    for ds in custom_order
]

# Dataset
data = {
    ("Schema1", "SKG3"): [91.11, 542.31, 31.47],
    ("Schema1", "MKG3"): [102.09, 590.98, 47.73],
    ("Schema1", "LKG3"): [107.93, 635.81, 49.18],
    ("Schema2", "SKG3"): [154.30, 854.15, 78.31],
    ("Schema2", "MKG3"): [258.44, 972.70, 91.83],
    ("Schema2", "LKG3"): [998.52, 1729.97, 617.10],
    ("Schema3", "SKG3"): [377.77, 2766.78, 65.02],
    ("Schema3", "MKG3"): [756.16, 4769.06, 112.96],
    ("Schema3", "LKG3"): [3423.93, 17495.30, 2770.38],
    ("Shape30", "DB50"): [578.27, 28116.61, 22.76],
    ("Shape30", "DB100"): [582.07, 26550.03, 23.82],
    ("Shape30", "DB1000"): [697.15, 32379.44, 24.25],
    ("InvSh", "InvDa"): [191.75, 1171.88, 17.20],
}

# Build DataFrame
index = pd.MultiIndex.from_tuples(data.keys(), names=["Shapes Graph", "Dataset"])
df = pd.DataFrame(list(data.values()), index=index, columns=["Use-Case 1", "Use-Case 2", "Use-Case 3"])

# Settings
use_cases = ["Use-Case 1", "Use-Case 2", "Use-Case 3"]
group_order = df.index.get_level_values(0).unique()
bar_width = 0.08
group_spacing = 0.05

# Plotting
fig, axes = plt.subplots(nrows=1, ncols=len(use_cases), figsize=(18, 5), sharey=True)

for idx, use_case in enumerate(use_cases):
    ax = axes[idx]
    ax.set_yscale("log")
    ax.set_title(use_case, fontsize=20)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    current_x = 0
    centers = []

    for shape_graph in group_order:
        try:
            group_data = df.loc[shape_graph][use_case]
        except KeyError:
            continue

        datasets = group_data.index.tolist()
        values = group_data.values.tolist()
        n = len(datasets)

        group_width = bar_width * n
        offsets = np.linspace(0, group_width - bar_width, n)
        group_start_x = current_x
        group_center = group_start_x + group_width / 2
        centers.append(group_center)

        for j, (ds, val) in enumerate(zip(datasets, values)):
            ax.bar(group_start_x + offsets[j], val, width=bar_width,
                   color=custom_dataset_colors.get(ds, "#999999"))

        current_x += group_width + group_spacing

    ax.set_xticks(centers)
    ax.tick_params(axis='y', labelsize=17)
    ax.set_xticklabels(group_order, rotation=45, ha='right', fontsize=18)

# Set axis labels
fig.supxlabel("Shapes Graph", fontsize=20)
fig.supylabel("Mean Query Time [ms] (log scale)", fontsize=20)

# Shared legend with bold inline "Dataset:"
fig.legend(
    handles=legend_handles,
    loc='lower center',
    ncol=8,
    bbox_to_anchor=(0.5, -0.12),
    frameon=True,
    fontsize=18
)

plt.tight_layout()
output_path = os.path.join(script_dir, "log_plot.pdf")
plt.savefig(output_path, format='pdf', bbox_inches='tight')
output_path
