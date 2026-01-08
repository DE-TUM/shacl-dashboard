import csv
from functions.shape_overview_service import (
    benchmark_function_execution_2,
    benchmark_function_execution_3,
    get_correlation_of_constraints_and_violations,
    get_number_of_violations_per_constraint_type_for_property_shape
)
from functions.homepage_service import (
    benchmark_function_execution,
    get_most_violated_node_shape
)

# Set parameters
data_graph = "mkg3"       # e.g., mkg3, lkg3, skg3
shapes_graph = "schema3"  # e.g., schema1, schema2, schema3
node_shape_uri = "http://swat.cse.lehigh.edu/onto/univ-bench.owl#CourseShape"

# Run benchmarks
result_uc1 = benchmark_function_execution(get_most_violated_node_shape)
result_uc2 = benchmark_function_execution_2(get_correlation_of_constraints_and_violations)
result_uc3 = benchmark_function_execution_3(
    lambda: get_number_of_violations_per_constraint_type_for_property_shape(node_shape_uri)
)

# Output base path
base_path = "C:\\Users\\johan_rvnnln\\OneDrive\\Desktop\\SHACL-Dashboard\\Demo\\shacl-dashboard\\backend\\evaluation"

# File paths following naming conventions
file_uc1 = f"{base_path}\\execution_time_use_case_1_{data_graph}_{shapes_graph}.csv"
file_uc2 = f"{base_path}\\execution_time_use_case_2_{data_graph}_{shapes_graph}.csv"
file_uc3 = f"{base_path}\\execution_time_use_case_3_{data_graph}_{shapes_graph}.csv"

# Write Use Case 1
with open(file_uc1, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Use Case", "Metric", "Value"])
    writer.writerow(["Use Case 1", "Most Violated Node Shape", str(result_uc1)])

# Write Use Case 2
with open(file_uc2, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Use Case", "Metric", "Value"])
    writer.writerow(["Use Case 2", "Correlation of Constraints and Violations", str(result_uc2)])

# Write Use Case 3
with open(file_uc3, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Use Case", "Metric", "Value"])
    writer.writerow(["Use Case 3", "Violations per Constraint Type for Property Shape", str(result_uc3)])

print(f"Execution times saved to:\n{file_uc1}\n{file_uc2}\n{file_uc3}")
