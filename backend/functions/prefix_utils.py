"""
Prefix Utilities Module

Lightweight utilities for extracting and caching RDF prefix declarations from Turtle files.
Designed to extract prefixes quickly by only reading file headers, not loading entire graphs.

Key functions:
- extract_prefixes_from_turtle_file: Extract @prefix declarations from Turtle file header
- extract_and_merge_prefixes: Extract and merge prefixes from multiple files
- cache_prefixes: Store extracted prefixes in global cache
- get_cached_prefixes: Retrieve cached prefixes for API responses
"""

import re
from pathlib import Path
from typing import Dict

# Global cache for extracted prefixes
_cached_prefixes: Dict[str, str] = {}

# Constants for prefix extraction behavior
# Maximum lines to read from file before stopping (prevents reading huge files)
# Turtle prefix declarations are typically in the first 10-50 lines
MAX_PREFIX_LINES_TO_READ = 500

# Number of consecutive non-prefix lines that indicates we're past the prefix section
# Prefixes are conventionally at the file header, so if we see 3+ non-prefix lines,
# we can safely assume we've left the prefix declarations section
CONSECUTIVE_NON_PREFIX_THRESHOLD = 3


def extract_prefixes_from_turtle_file(file_path: str, max_lines: int = MAX_PREFIX_LINES_TO_READ) -> Dict[str, str]:
    """
    Extract @prefix declarations from a Turtle file by reading only the header.
    
    This is extremely fast - only reads until it finds no more prefix declarations,
    typically the first 10-50 lines. Does NOT parse the entire graph.
    
    Args:
        file_path: Path to the .ttl file
        max_lines: Maximum lines to read (default MAX_PREFIX_LINES_TO_READ, stops earlier if no more prefixes)
        
    Returns:
        dict: Dictionary of {prefix: namespace_uri}
        
    Example:
        >>> prefixes = extract_prefixes_from_turtle_file("shapes.ttl")
        >>> print(prefixes)
        {'dbo': 'http://dbpedia.org/ontology/', 'sh': 'http://www.w3.org/ns/shacl#', ...}
    """
    prefixes = {}
    
    # Regex patterns for Turtle prefix declarations
    # Matches: @prefix dbo: <http://dbpedia.org/ontology/> .
    prefix_pattern = re.compile(r'@prefix\s+([^:]+):\s+<([^>]+)>\s*\.')
    # Also support SPARQL-style: PREFIX dbo: <http://dbpedia.org/ontology/>
    sparql_prefix_pattern = re.compile(r'PREFIX\s+([^:]+):\s+<([^>]+)>', re.IGNORECASE)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            consecutive_non_prefix_lines = 0
            
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check for @prefix declarations
                match = prefix_pattern.match(line)
                if match:
                    prefix, namespace = match.groups()
                    prefixes[prefix] = namespace
                    consecutive_non_prefix_lines = 0
                    continue
                
                # Check for PREFIX declarations (SPARQL style)
                match = sparql_prefix_pattern.match(line)
                if match:
                    prefix, namespace = match.groups()
                    prefixes[prefix] = namespace
                    consecutive_non_prefix_lines = 0
                    continue
                
                # If we hit a line that's not a prefix and not empty/comment,
                # we might be past the prefix section (they're typically at the top)
                if line and not line.startswith('@') and not line.upper().startswith('PREFIX'):
                    consecutive_non_prefix_lines += 1
                    # If we've seen multiple consecutive non-prefix lines, we're definitely past prefixes
                    if consecutive_non_prefix_lines >= CONSECUTIVE_NON_PREFIX_THRESHOLD:
                        break
        
        return prefixes
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except Exception as e:
        print(f"Error extracting prefixes from {file_path}: {e}")
        return {}


def extract_and_merge_prefixes(*file_paths: str) -> Dict[str, str]:
    """
    Extract prefixes from multiple Turtle files and merge them.
    
    Args:
        *file_paths: Variable number of file paths
        
    Returns:
        dict: Merged dictionary of all prefixes from all files
        
    Example:
        >>> prefixes = extract_and_merge_prefixes("shapes.ttl", "report.ttl")
        >>> print(len(prefixes))
        15
    """
    all_prefixes = {}
    
    for file_path in file_paths:
        if file_path and Path(file_path).exists():
            file_prefixes = extract_prefixes_from_turtle_file(file_path)
            all_prefixes.update(file_prefixes)
            print(f"Extracted {len(file_prefixes)} prefixes from {Path(file_path).name}")
    
    # Ensure essential SHACL prefix exists
    if 'sh' not in all_prefixes:
        all_prefixes['sh'] = 'http://www.w3.org/ns/shacl#'
    
    return all_prefixes


def cache_prefixes(prefixes: Dict[str, str]):
    """
    Store prefixes in global cache.
    
    Args:
        prefixes: Dictionary of prefix mappings to cache
    """
    global _cached_prefixes
    _cached_prefixes = prefixes.copy()
    print(f"Cached {len(_cached_prefixes)} prefixes: {list(_cached_prefixes.keys())}")


def get_cached_prefixes() -> Dict[str, str]:
    """
    Retrieve cached prefixes.
    
    Returns:
        dict: Copy of cached prefix mappings
    """
    return _cached_prefixes.copy()


def clear_prefix_cache():
    """
    Clear the prefix cache.
    Useful when loading new data files.
    """
    global _cached_prefixes
    _cached_prefixes = {}
    print("Prefix cache cleared")


def extract_prefixes_from_sparql_graphs(
    endpoint_url: str,
    graph_uris: list,
    common_prefixes: dict = None
) -> Dict[str, str]:
    """
    Extract prefixes by querying unique URI namespaces from SPARQL graphs.
    This complements file-based extraction by discovering all URIs actually used in the graphs.
    
    Args:
        endpoint_url: SPARQL endpoint URL
        graph_uris: List of graph URIs to query
        common_prefixes: Dict of common prefix mappings to check against
        
    Returns:
        dict: Discovered prefix mappings
    """
    import requests
    from collections import Counter
    
    # Common RDF prefixes (generic, non-domain-specific only)
    if common_prefixes is None:
        common_prefixes = {
            'http://shaclshapes.org/': 'shs',
            'http://www.w3.org/ns/shacl#': 'sh',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
            'http://www.w3.org/2000/01/rdf-schema#': 'rdfs',
            'http://www.w3.org/2001/XMLSchema#': 'xsd',
            'http://www.w3.org/2002/07/owl#': 'owl',
            'http://xmlns.com/foaf/0.1/': 'foaf',
            'http://rdfs.org/ns/void#': 'void',
            'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#': 'dul',
        }
    
    discovered_namespaces = set()
    
    # Query to get all distinct subject, predicate, and object URIs from each graph
    for graph_uri in graph_uris:
        query = f"""
        SELECT DISTINCT ?uri
        FROM <{graph_uri}>
        WHERE {{
          {{
            ?uri ?p ?o .
            FILTER(isURI(?uri) && !STRSTARTS(STR(?uri), "nodeID://"))
          }} UNION {{
            ?s ?uri ?o .
            FILTER(isURI(?uri) && !STRSTARTS(STR(?uri), "nodeID://"))
          }} UNION {{
            ?s ?p ?uri .
            FILTER(isURI(?uri) && !STRSTARTS(STR(?uri), "nodeID://"))
          }}
        }}
        LIMIT 50000
        """
        
        try:
            response = requests.get(
                endpoint_url,
                params={"query": query, "format": "json"},
                timeout=30
            )
            response.raise_for_status()
            results = response.json()["results"]["bindings"]
            
            for binding in results:
                if "uri" in binding:
                    uri = binding["uri"]["value"]
                    discovered_namespaces.add(uri)
                    
            print(f"Discovered {len(results)} URIs from {graph_uri}")
                    
        except Exception as e:
            print(f"Error querying graph {graph_uri}: {e}")
    
    # Extract namespace patterns from discovered URIs
    namespace_counts = Counter()
    for uri in discovered_namespaces:
        # Try to split at # or last /
        if '#' in uri:
            namespace = uri.rsplit('#', 1)[0] + '#'
        elif '/' in uri:
            namespace = uri.rsplit('/', 1)[0] + '/'
        else:
            continue
        namespace_counts[namespace] += 1
    
    # Map namespaces to prefixes
    prefixes = {}
    import re
    
    for namespace, count in namespace_counts.items():
        # Check if it matches a known generic prefix
        if namespace in common_prefixes:
            prefix = common_prefixes[namespace]
            prefixes[prefix] = namespace
        else:
            # General pattern matching for various namespace patterns
            
            # DBpedia base resources: http://dbpedia.org/resource/ -> dbr
            if namespace == 'http://dbpedia.org/resource/':
                prefixes['dbr'] = namespace
            # DBpedia base ontology: http://dbpedia.org/ontology/ -> dbo
            elif namespace == 'http://dbpedia.org/ontology/':
                prefixes['dbo'] = namespace
            # DBpedia base property: http://dbpedia.org/property/ -> dbp
            elif namespace == 'http://dbpedia.org/property/':
                prefixes['dbp'] = namespace
            # YAGO classes: http://dbpedia.org/class/yago/ -> yago
            elif namespace == 'http://dbpedia.org/class/yago/':
                prefixes['yago'] = namespace
            
            # Language-specific DBpedia resources: http://{lang}.dbpedia.org/resource/ -> dbr-{lang}
            else:
                match = re.match(r'http://([a-z]{2,3})\.dbpedia\.org/resource/', namespace)
                if match:
                    lang_code = match.group(1)
                    prefixes[f'dbr-{lang_code}'] = namespace
                    continue
                
                # Language-specific DBpedia ontology: http://{lang}.dbpedia.org/ontology/ -> dbo-{lang}
                match = re.match(r'http://([a-z]{2,3})\.dbpedia\.org/ontology/', namespace)
                if match:
                    lang_code = match.group(1)
                    prefixes[f'dbo-{lang_code}'] = namespace
                    continue
                
                # Language-specific DBpedia property: http://{lang}.dbpedia.org/property/ -> dbp-{lang}
                match = re.match(r'http://([a-z]{2,3})\.dbpedia\.org/property/', namespace)
                if match:
                    lang_code = match.group(1)
                    prefixes[f'dbp-{lang_code}'] = namespace
    
    print(f"Extracted {len(prefixes)} prefixes from SPARQL graphs: {list(prefixes.keys())}")
    return prefixes
