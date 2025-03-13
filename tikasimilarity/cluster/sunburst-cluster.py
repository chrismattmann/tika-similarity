#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# TIKA SIMILARITY - SUNBURST CLUSTER GENERATOR
#
# This script converts a CSV file containing document similarity scores into
# a hierarchical JSON structure suitable for D3.js sunburst visualization.
#
# Required CSV format:
# x-coordinate,y-coordinate,Similarity_score
# /path/to/doc1.pdf,/path/to/doc2.pdf,0.85
# 
# Example usage:
# python sunburst-cluster.py --input similarity.csv --output clusters.json --clusters 5
#
# After generating clusters.json, you can view the visualization by:
# 1. Placing clusters.json in the same directory as sunburst.html
# 2. Starting a web server: python -m http.server 8000
# 3. Opening http://localhost:8000/sunburst.html in a web browser
#

import json
import csv
import argparse
import os
import sys
import numpy as np
from collections import defaultdict

def create_sunburst_json(csv_file, output_file, num_clusters=5):
    """Convert similarity CSV to hierarchical JSON for sunburst visualization
    
    Args:
        csv_file: Path to input CSV file with similarity scores
        output_file: Path where JSON output will be written
        num_clusters: Number of document clusters to create
        
    Returns:
        None. Results are written to the output file.
    """
    # Validate input file
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Input file not found: {csv_file}")
    
    # Validate CSV has required columns
    with open(csv_file, 'r') as f:
        header = f.readline().strip().split(',')
        if 'x-coordinate' not in header or 'y-coordinate' not in header or 'Similarity_score' not in header:
            raise ValueError("CSV must contain columns 'x-coordinate', 'y-coordinate', and 'Similarity_score'")
    
    # Read similarity data
    docs_set = set()
    sim_dict = {}
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row['x-coordinate']
                target = row['y-coordinate']
                
                # Safely convert score to float
                try:
                    score = float(row['Similarity_score'])
                except ValueError:
                    print(f"Warning: Invalid similarity score '{row['Similarity_score']}' for {source} -> {target}")
                    score = 0.0
                
                docs_set.add(source)
                docs_set.add(target)
                
                # Store similarity scores in both directions
                sim_dict[(source, target)] = score
                sim_dict[(target, source)] = score
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file: {str(e)}")
    
    # Verify we have documents
    if not docs_set:
        raise ValueError("No valid document pairs found in CSV file")
    
    print(f"Found {len(docs_set)} unique documents")
    
    # Convert to list for consistent indexing
    docs_list = list(docs_set)
    n_docs = len(docs_list)
    
    # Create simple clustering based on similarity thresholds
    clusters = defaultdict(list)
    assigned = set()
    
    # Sort document pairs by similarity (highest first)
    print("Computing document similarities...")
    sorted_pairs = sorted([(d1, d2) for d1 in docs_list for d2 in docs_list if d1 != d2], 
                         key=lambda pair: sim_dict.get((pair[0], pair[1]), 0), 
                         reverse=True)
    
    # Assign documents to clusters
    print(f"Creating {num_clusters} clusters...")
    cluster_id = 0
    for d1, d2 in sorted_pairs:
        if d1 not in assigned and d2 not in assigned:
            # Start a new cluster with this pair
            clusters[cluster_id].append(d1)
            clusters[cluster_id].append(d2)
            assigned.add(d1)
            assigned.add(d2)
            cluster_id += 1
            
            # Stop when we have enough clusters
            if cluster_id >= num_clusters:
                break
    
    # Assign remaining documents to nearest cluster
    print("Assigning remaining documents to clusters...")
    for doc in docs_list:
        if doc not in assigned:
            # Find best cluster for this document
            best_score = -1
            best_cluster = 0
            
            for c_id, c_docs in clusters.items():
                # Calculate average similarity to this cluster
                avg_sim = sum(sim_dict.get((doc, c_doc), 0) for c_doc in c_docs) / len(c_docs) if c_docs else 0
                if avg_sim > best_score:
                    best_score = avg_sim
                    best_cluster = c_id
            
            # Assign to best cluster
            clusters[best_cluster].append(doc)
            assigned.add(doc)
    
    # Create hierarchical structure for sunburst chart
    root = {
        "name": "Documents",
        "children": []
    }
    
    # Add clusters to the hierarchy
    for cluster_id, docs in clusters.items():
        cluster_node = {
            "name": f"Cluster {cluster_id + 1}",
            "children": []
        }
        
        # Add documents to each cluster
        for doc in docs:
            # Calculate avg similarity to other docs in same cluster
            avg_sim = 0
            if len(docs) > 1:
                avg_sim = sum(sim_dict.get((doc, other), 0) 
                             for other in docs if other != doc) / (len(docs) - 1)
            
            # Use filename only for display
            doc_name = os.path.basename(doc)
            
            # Add document node
            cluster_node["children"].append({
                "name": doc_name,
                "path": doc,
                "size": max(10, avg_sim * 100)  # Scale for visibility
            })
        
        root["children"].append(cluster_node)
    
    # Write to JSON file
    try:
        with open(output_file, 'w') as f:
            json.dump(root, f, indent=2)
        print(f"Created hierarchical JSON for sunburst: {output_file}")
    except Exception as e:
        raise IOError(f"Error writing output file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create hierarchical JSON for sunburst visualization')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--clusters', type=int, default=5, help='Number of clusters to create')
    
    args = parser.parse_args()
    
    try:
        create_sunburst_json(args.input, args.output, args.clusters)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)