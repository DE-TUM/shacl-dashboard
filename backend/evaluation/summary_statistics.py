import csv
from functions.homepage_service import (
    get_number_of_violations_in_validation_report,
    count_triples,
    get_number_of_node_shapes_with_violations,
    get_number_of_node_shapes,
    get_number_of_focus_nodes_in_validation_report,
    get_number_of_paths_with_violations,
    get_number_of_paths_in_shapes_graph,
    get_distinct_constraints_count_in_shapes,
    get_distribution_of_violations_per_constraint_component
)

# Set graph names
shapes_graph_name = "Shape30"  
data_graph = "DB50"           

# Collect runtime evaluation metrics
results = {
    "Number of Violations in Report": get_number_of_violations_in_validation_report(),
    "Triple Count": count_triples(),
    "Node Shapes with Violations": get_number_of_node_shapes_with_violations(),
    "Total Node Shapes": get_number_of_node_shapes(),
    "Focus Nodes in Validation Report": get_number_of_focus_nodes_in_validation_report(),
    "Paths with Violations": get_number_of_paths_with_violations(),
    "Total Paths in Shapes Graph": get_number_of_paths_in_shapes_graph(),
    "Distinct Constraints in Shapes Graph": get_distinct_constraints_count_in_shapes(),
    "Distribution of Violations per Constraint": str(get_distribution_of_violations_per_constraint_component())
}

# Construct dynamic file path
output_path = f"C:\\Users\\johan_rvnnln\\OneDrive\\Desktop\\SHACL-Dashboard\\Demo\\shacl-dashboard\\backend\\evaluation\\summary_statistics_{shapes_graph_name}_{data_graph}.csv"

# Write results to CSV
with open(output_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Shapes Graph", shapes_graph_name])
    writer.writerow(["Data Graph", data_graph])
    writer.writerow([])  # empty row for readability
    for key, value in results.items():
        writer.writerow([key, value])

print(f"Runtime metrics saved to: {output_path}")