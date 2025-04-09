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
#

# Computing pairwise jaccard similarity for a given directory of files

from tika import parser
import os, itertools, argparse, csv
from functools import reduce
import sys
import json
from tqdm import tqdm

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    if acceptTypes:
        filtered_files = []
        for filename in filename_list:
            metadata = parser.from_file(filename).get("metadata", {})
            content_type = str(metadata.get("Content-Type", "").encode('utf-8').decode('utf-8')).split('/')[-1]
            if content_type in acceptTypes:
                filtered_files.append(filename)
        filename_list = filtered_files
    else:
        print("Accepting all MIME Types.....")

    return filename_list

def computeScores(inputDir, outCSV, acceptTypes):
    if sys.version_info[0] >= 3:
        openMode = "w"
    else:
        openMode = "wb"
        
    with open(outCSV, openMode) as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        files_list = filterFiles(inputDir, acceptTypes)
        
        parsed_results = {}
        for filename in tqdm(files_list, desc="Parsing files", unit="file"):
            parsed_results[filename] = parser.from_file(filename)

        files_tuple = list(itertools.combinations(files_list, 2))

        for file1, file2 in tqdm(files_tuple, desc="Computing file similarities", unit="pair"):
            f1MetaData = parsed_results[file1]["metadata"]
            f2MetaData = parsed_results[file2]["metadata"]

            isCoExistant = lambda k: (k in f2MetaData) and (f1MetaData[k] == f2MetaData[k])
            intersection = reduce(lambda m, k: (m + 1) if isCoExistant(k) else m, list(f1MetaData.keys()), 0)

            union = len(list(f1MetaData.keys())) + len(list(f2MetaData.keys())) - intersection
            jaccard = float(intersection) / union if union > 0 else 0.0

            a.writerow([file1, file2, jaccard])

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

        obj_pairs = list(itertools.combinations(object_list, 2))
        for obj1, obj2 in tqdm(obj_pairs, desc="Computing JSON similarities", unit="pair"):
            similarity_score = compute_jaccard_similarity(obj1, obj2, allKeys)
            writer.writerow([obj1.get('id', 'Unknown'), obj2.get('id', 'Unknown'), similarity_score])

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

if __name__ == "__main__":
    argParser = argparse.ArgumentParser('Jaccard similarity based file metadata')
    argParser.add_argument('--inputDir', required=False, help='Path to directory containing files')
    argParser.add_argument('--inputFile', required=False, help='Path to input JSON file')
    argParser.add_argument('--outCSV', required=True, help='Path to directory for storing the output CSV file')
    argParser.add_argument('--jsonKey', required=False, help='JSON object list key (required if using --inputFile).')
    argParser.add_argument('--allKeys', action='store_true', help='Include all keys in Jaccard similarity computation')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')

    args = argParser.parse_args()

    if args.inputDir:
        computeScores(args.inputDir, args.outCSV, args.accept)
    elif args.inputFile:
        if not args.jsonKey:
            print("Error: --jsonKey is required when using --inputFile.")
            sys.exit(1)
        process_json(args.inputFile, args.outCSV, args.jsonKey, args.allKeys)
    else:
        print("Error: Either --inputFile or --inputDir must be provided.")
        sys.exit(1)
