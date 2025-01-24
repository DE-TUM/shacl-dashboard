import subprocess
from virtuoso_service import *

#load_graphs("/Users/kejin/Developer/Trav-Exp/source/Datasets/", "shape30_clean.ttl", "EnDe50_result_.ttl")
#result = get_violations_for_shape_name("http://shaclshapes.org/seeAlsoSnookerPlayerShapeProperty","http://ex.org/ValidationReports")

#result = map_property_shapes_to_node_shapes("http://ex.org/ValidationReports", "http://ex.org/ShapesGraph")

result = get_shape_from_shapes_graph(["http://shaclshapes.org/AmphibianShape"])
print(len(result["http://shaclshapes.org/AmphibianShape"]["propertyShapes"]))
