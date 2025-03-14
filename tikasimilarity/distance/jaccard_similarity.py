import argparse
import json
import csv
import itertools
import os
import sys
from functools import reduce
from tqdm import tqdm
from tika import parser 

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    parsed_results = {filename: parser.from_file(filename) for filename in filename_list}

    if acceptTypes:
        filename_list = [
            filename for filename in filename_list 
            if str(parsed_results[filename]['metadata']['Content-Type'].encode('utf-8').decode('utf-8')).split('/')[-1] in acceptTypes
        ]
    else:
        print("Accepting all MIME Types.....")

    return filename_list, parsed_results

def compute_jaccard_similarity(obj1, obj2, allKeys=False):
    keys1 = set(obj1.keys())
    keys2 = set(obj2.keys())

    if allKeys:
        union = keys1 | keys2
        intersection = {key for key in keys1 & keys2 if obj1[key] == obj2[key]}
    else:
        intersection = {key for key in keys1 & keys2 if obj1[key] == obj2[key]}
        union = keys1 & keys2  

    return len(intersection) / len(union) if len(union) > 0 else 0.0

def process_json(input_file, output_csv, json_key, allKeys):
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

def computeScores(inputDir, outCSV, acceptTypes):
    if sys.version_info[0] >= 3:
        openMode = "w"
    else:
        openMode = "wb"
        
    with open(outCSV, openMode) as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        files_list, parsed_results = filterFiles(inputDir, acceptTypes)

        files_tuple = itertools.combinations(files_list, 2)

        for file1, file2 in files_tuple:
            f1MetaData = parsed_results[file1]["metadata"]
            f2MetaData = parsed_results[file2]["metadata"]

            isCoExistant = lambda k: (k in f2MetaData) and (f1MetaData[k] == f2MetaData[k])
            intersection = reduce(lambda m, k: (m + 1) if isCoExistant(k) else m, list(f1MetaData.keys()), 0)

            union = len(list(f1MetaData.keys())) + len(list(f2MetaData.keys())) - intersection
            jaccard = float(intersection) / union if union > 0 else 0.0

            a.writerow([file1, file2, jaccard])

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
