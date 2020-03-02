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
from vector import Vector
import os, itertools, argparse, csv
from requests import ConnectionError
from time import sleep
import json

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    filename_list = [filename for filename in filename_list if parser.from_file(filename)]
    if acceptTypes:
        filename_list = [filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8')).split('/')[-1] in acceptTypes]
    else:
        print "Accepting all MIME Types....."

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
        intersection = reduce(lambda m,k: (m + 1) if isCoExistant(k) else m, f1MetaData.keys(), 0)


        union = len(f1MetaData.keys()) + len(f2MetaData.keys()) - intersection
        jaccard = float(intersection) / union

        a.writerow([file1, file2, jaccard])

def computeScores2(inputFile, outCSV):
    with open(outCSV, "wb") as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])

        file1_parsedData = parser.from_file(inputFile)
        row_list = json.loads(file1_parsedData["content"])

        rows_tuple = itertools.combinations(row_list, 2)
        for row1, row2 in rows_tuple:

            try:                
                isCoExistant = lambda k: (k in row2) and (row1[k] == row2[k])
                intersection = reduce(lambda m, k: (m + 1) if isCoExistant(k) else m, row1.keys(), 0)
                
                union = len(row1.keys()) + len(row2.keys()) - intersection
                jaccard = float(intersection) / union

                a.writerow([row_list.index(row1), row_list.index(row2), jaccard])
            except ConnectionError:
                sleep(1)
            except KeyError:
                continue

if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Jaccard similarity based file metadata')
    argParser.add_argument('--inputFile', required=False, help='path to file')
    argParser.add_argument('--inputDir', required=False, help='path to directory containing files')
    argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing pair-wise Jaccard similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    if args.inputDir and args.outCSV:
        computeScores(args.inputDir, args.outCSV, args.accept)
    if args.inputFile and args.outCSV:
        computeScores2(args.inputFile, args.outCSV)