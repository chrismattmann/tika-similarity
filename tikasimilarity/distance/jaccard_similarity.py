import argparse
import json
import csv
import itertools
from tqdm import tqdm

def compute_jaccard_similarity(obj1, obj2, allKeys=False):
    """Computes Jaccard similarity between two JSON objects."""
    keys1 = set(obj1.keys())
    keys2 = set(obj2.keys())

    if allKeys:
        # Consider all keys, including those unique to each object
        union = keys1 | keys2
        intersection = {key for key in keys1 & keys2 if obj1[key] == obj2[key]}
    else:
        # Only consider intersecting keys for similarity
        intersection = {key for key in keys1 & keys2 if obj1[key] == obj2[key]}
        union = keys1 & keys2  # Only common keys

    return len(intersection) / len(union) if len(union) > 0 else 0.0

def process_json(input_file, output_csv, json_key, allKeys):
    """Processes a JSON file and computes Jaccard similarity for pairs of objects."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if json_key:
        object_list = data.get(json_key, [])
    else:
        print("Error: Please specify a valid JSON key using --jsonKey")
        return
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        for obj1, obj2 in tqdm(itertools.combinations(object_list, 2), total=len(object_list) * (len(object_list) - 1) // 2, desc="Computing similarities"):
            similarity_score = compute_jaccard_similarity(obj1, obj2, allKeys)
            writer.writerow([obj1.get('id', 'Unknown'), obj2.get('id', 'Unknown'), similarity_score])

def main():
    argParser = argparse.ArgumentParser(description="Compute pairwise similarity for JSON objects.")
    argParser.add_argument('--inputFile', required=True, help='Path to the input JSON file.')
    argParser.add_argument('--outCSV', required=True, help='Path to the output CSV file.')
    argParser.add_argument('--jsonKey', required=True, help='JSON object list key')
    argParser.add_argument('--allKeys', action='store_true', help='Include all keys in Jaccard similarity computation')

    args = argParser.parse_args()

    process_json(args.inputFile, args.outCSV, args.jsonKey, args.allKeys)

if __name__ == "__main__":
    main()
