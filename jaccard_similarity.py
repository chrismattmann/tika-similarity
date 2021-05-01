#!/usr/bin/env python2.7
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
import json
import os, itertools, argparse, csv
from functools import reduce


def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    filename_list = [filename for filename in filename_list if parser.from_file(filename)]
    if acceptTypes:
        filename_list = [filename for filename in filename_list if str(
            parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8').decode('utf-8')).split('/')[
            -1] in acceptTypes]
    else:
        print("Accepting all MIME Types.....")

    return filename_list


def computeScores(inputDir, outCSV, acceptTypes):

    with open(outCSV, "wb") as outF:
      a = csv.writer(outF, delimiter=',')
      a.writerow(["x-coordinate","y-coordinate","Similarity_score"])

      files_tuple = itertools.combinations(filterFiles(inputDir, acceptTypes), 2)

      for file1, file2 in files_tuple:
        f1MetaData = parser.from_file(file1)["metadata"]
        f2MetaData = parser.from_file(file2)["metadata"]

        isCoExistant = lambda k: ( k in f2MetaData) and ( f1MetaData[k] == f2MetaData[k] )
        intersection = reduce(lambda m,k: (m + 1) if isCoExistant(k) else m, list(f1MetaData.keys()), 0)


        union = len(list(f1MetaData.keys())) + len(list(f2MetaData.keys())) - intersection
        jaccard = float(intersection) / union

        a.writerow([file1, file2, jaccard])


def computeScoresJson(inputDir, outCSV, acceptTypes):
    with open(outCSV, "w") as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        files_tuple = itertools.combinations(filterFiles(inputDir, acceptTypes), 2)

        for file1, file2 in files_tuple:
            if not file1.endswith('json'):
                continue
            if not file2.endswith('json'):
                continue
            with open(file1, 'r') as f1:
                f1MetaData = json.load(f1)
                if type(f1MetaData) == dict:
                    for k, v in f1MetaData.items():
                        f1MetaData[k] = str(v)
                elif type(f1MetaData) == list:
                    file1_metadata = f1MetaData
                    f1MetaData = {}
                    for item in file1_metadata:
                        for k, v in item.items():
                            f1MetaData[k] = str(v)
            with open(file2, 'r') as f2:
                f2MetaData = json.load(f2)
                if type(f2MetaData) == dict:
                    for k, v in f2MetaData.items():
                        f2MetaData[k] = str(v)
                elif type(f2MetaData) == list:
                    file2_metadata = f2MetaData
                    f2MetaData = {}
                    for item in file2_metadata:
                        for k, v in item.items():
                            f2MetaData[k] = str(v)

            isCoExistant = lambda k: (k in f2MetaData) and (f1MetaData[k] == f2MetaData[k])
            intersection = reduce(lambda m, k: (m + 1) if isCoExistant(k) else m, list(f1MetaData.keys()), 0)

            union = len(list(f1MetaData.keys())) + len(list(f2MetaData.keys())) - intersection
            jaccard = float(intersection) / union

            a.writerow([file1, file2, jaccard])


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Jaccard similarity based file metadata')
    argParser.add_argument('--inputDir', required=False, help='path to directory containing files')
    argParser.add_argument('--jsonDir', required=False, help='path to directory containing all the json metadata files')
    argParser.add_argument('--outCSV', required=True,
                           help='path to directory for storing the output CSV File, containing pair-wise Jaccard similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str,
                           help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    if args.inputDir and args.outCSV:
        computeScores(args.inputDir, args.outCSV, args.accept)
    if args.jsonDir and args.outCSV:
        computeScoresJson(args.jsonDir, args.outCSV, args.accept)
