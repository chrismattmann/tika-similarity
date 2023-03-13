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


def computeScores(inputDir, outCSV, acceptTypes):

    if sys.version_info[0] >= 3:
        openMode = "w"
    else:
        openMode = "wb"
        
    
    with open(outCSV, openMode) as outF:
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


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Jaccard similarity based file metadata')
    argParser.add_argument('--inputDir', required=True, help='path to directory containing files')
    argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing pair-wise Jaccard similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    if args.inputDir and args.outCSV:
        computeScores(args.inputDir, args.outCSV, args.accept)
