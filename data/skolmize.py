from rdflib import Graph

# Load your shapes graph
g = Graph()
g.parse('schema1.ttl', format='turtle')
# Set your authority (your base URL)
authority = "http://example.org/shapes/"
# Skolemize all blank nodes
g_new = g.skolemize(authority=authority, basepath=None)
# Save the updated graph
g_new.serialize(destination='schema1_updated.ttl', format='turtle')