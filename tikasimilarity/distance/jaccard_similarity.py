import argparse
import json
import csv
import os
from itertools import combinations
from tqdm import tqdm
from tika import parser

def filterFiles(inputDir, acceptTypes):
    filename_list = []
    
    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))
    
    filename_list = [filename for filename in filename_list if parser.from_file(filename)]
    if acceptTypes:
        filename_list = [filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8').decode('utf-8')).split('/')[-1] in acceptTypes]
    else:
        print("Accepting all MIME Types.....")
    
    return filename_list

def compute_jaccard_similarity(obj1, obj2):
    """Computes Jaccard similarity based on exact key-value matches."""
    keys1 = set(obj1.keys())
    keys2 = set(obj2.keys())
    
    intersection = sum(1 for key in keys1 & keys2 if obj1[key] == obj2[key])
    union = len(keys1 | keys2)
    
    return intersection / union if union > 0 else 0.0

def process_json(input_file, output_csv, json_key):
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

        for obj1, obj2 in tqdm(combinations(object_list, 2), total=len(object_list) * (len(object_list) - 1) // 2, desc="Computing similarities"):
            similarity_score = compute_jaccard_similarity(obj1, obj2)
            writer.writerow([obj1.get('id', 'Unknown'), obj2.get('id', 'Unknown'), similarity_score])

def computeScores(inputDir, outCSV, acceptTypes):
    """Processes file metadata and computes Jaccard similarity between metadata attributes."""
    with open(outCSV, "w", newline='', encoding='utf-8') as outF:
        writer = csv.writer(outF, delimiter=',')
        writer.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        files_tuple = list(combinations(filterFiles(inputDir, acceptTypes), 2))
        
        for file1, file2 in tqdm(files_tuple, desc="Processing files"):
            f1MetaData = parser.from_file(file1)["metadata"]
            f2MetaData = parser.from_file(file2)["metadata"]
            
            isCoExistant = lambda k: (k in f2MetaData) and (f1MetaData[k] == f2MetaData[k])
            intersection = sum(1 for k in f1MetaData.keys() if isCoExistant(k))
            
            union = len(f1MetaData.keys()) + len(f2MetaData.keys()) - intersection
            jaccard = float(intersection) / union if union > 0 else 0.0
            
            writer.writerow([file1, file2, jaccard])

def main():
    argParser = argparse.ArgumentParser(description="Compute pairwise similarity for JSON objects or file metadata.")
    argParser.add_argument('--inputFile', help='Path to the input JSON file.')
    argParser.add_argument('--inputDir', help='Path to the directory containing files.')
    argParser.add_argument('--outCSV', required=True, help='Path to the output CSV file.')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    argParser.add_argument('--jsonKey', required=False, help='JSON object list key')

    args = argParser.parse_args()
    
    if args.inputFile and args.jsonKey:
        process_json(args.inputFile, args.outCSV, args.jsonKey)
    elif args.inputDir:
        computeScores(args.inputDir, args.outCSV, args.accept)
    else:
        print("Error: Either --inputFile (with --jsonKey) or --inputDir must be specified.")

if __name__ == "__main__":
    main()