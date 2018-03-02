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

import json
import argparse
import csv


def createCorrelationMatrix(inputCSV):
    row = []
    csvPath = inputCSV  # Input Path to csv file
    with open(csvPath, "r") as f:
        lines = csv.reader(f.read().splitlines(), delimiter=' ')
        for line in lines:
            row.append(line)

    data = {}
    for i in range(len(row)):
        if "x-coordinate" in row[i][0].split(","):
            continue
        else:
            column = row[i][0].split(",")
            if not column[0] in data:
                data[column[0]] = {}
            data[column[0]][column[1]] = column[2]
    matrix = []
    unique_states = data.keys()
    for row in unique_states:
        row_data = []
        for col in unique_states:
            if row == col:
                row_data.append(1.0)
            else:
                if row in data and col in data[row]:
                    row_data.append(round(float(data[row][col]),2))
                else:
                    row_data.append(0.0)
        matrix.append(row_data)

    matrixJson = {"matrix": matrix, "states": unique_states}
    with open("correlation-matrix.json", "w") as f:  # Pass the json file as input to correlation-matrix-d3.html
        f.write(json.dumps(matrixJson))


if __name__ == '__main__':
    argParser = argparse.ArgumentParser('Edit/Cosine Similarity Circle Packing')
    argParser.add_argument('--inputCSV', required=True,
                           help='path to directory containing CSV File, containing pair-wise similarity scores based on edit/cosine similarity distance')
    args = argParser.parse_args()

    createCorrelationMatrix(args.inputCSV)
