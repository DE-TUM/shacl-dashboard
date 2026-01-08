import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch

# Set Seaborn base style
sns.set_theme(style="whitegrid")
palette = sns.color_palette("muted")

script_dir = os.path.dirname(os.path.abspath(__file__))

custom_dataset_colors = {
    "DB100": "#984ea3",
    "DB1000": "#377eb8",
    "DB50": "#e41a1c",
    "InvDa": "#a65628",
    "LKG3": "#ff7f0e",
    "MKG3": "#4daf4a",
    "SKG3": "#1f77b4",
}

legend_handles = [
    Patch(facecolor=color, label=ds)
    for ds, color in custom_dataset_colors.items()
]

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

index = pd.MultiIndex.from_tuples(data.keys(), names=["Shapes Graph", "Dataset"])
df = pd.DataFrame(list(data.values()), index=index, columns=["Use-Case 1", "Use-Case 2", "Use-Case 3"])

use_cases = ["Use-Case 1", "Use-Case 2", "Use-Case 3"]
bar_width = 0.03
inter_group_spacing = 0.01

for use_case in use_cases:
    use_case_data = df[use_case].reset_index()
    grouped = use_case_data.groupby("Shapes Graph")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_title(f"{use_case}", fontsize=21, pad=12)
    x_ticks = []
    x_labels = []

    current_x = 0

    for shape_graph, group in grouped:
        datasets = group["Dataset"].tolist()
        values = group[use_case].tolist()
        num_bars = len(datasets)

        group_width = bar_width * num_bars
        group_start_x = current_x
        group_center = group_start_x + (num_bars - 1) * bar_width / 2

        offsets = np.arange(num_bars) * bar_width

        for i, (ds, val) in enumerate(zip(datasets, values)):
            ax.bar(
                group_start_x + offsets[i],
                val,
                width=bar_width,
                color=custom_dataset_colors.get(ds, "#999999")
            )

        x_ticks.append(group_center)
        x_labels.append(shape_graph)

        current_x += group_width + inter_group_spacing  # move to next group

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=45, ha='center', fontsize=21)
    ax.set_ylabel("Mean Query Time [ms]", fontsize=22)
    ax.tick_params(axis='y', labelsize=19)
    ax.set_xlabel("Shapes Graph", fontsize=22)
    ax.set_yscale("log")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Static full legend
    ax.legend(
        handles=legend_handles,
        title="Dataset",
        loc="upper right",
        bbox_to_anchor=(0.205, 0.98),
        borderaxespad=0,
        frameon=True,
        fontsize=15,
        title_fontsize=16
    )
    
    plt.tight_layout()
    filename = os.path.join(script_dir, f"{use_case.replace(' ', '_')}_log_plot.pdf")
    plt.savefig(filename, format='pdf', bbox_inches='tight')
    # plt.show()  # Uncomment for preview
