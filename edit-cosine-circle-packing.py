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
import sys
import csv

row=[]
csvPath = sys.argv[1]       #Input Path to csv file
with open(csvPath,"r") as f:
    lines = csv.reader(f.read().splitlines(), delimiter=' ')
    for line in lines:
        row.append(line)

data={}
for i in range(len(row)):
    if "x-coordinate" in row[i][0].split(","):
        continue
    else:
        column = row[i][0].split(",")
        data[column[0]]=[]

for i in range(len(row)):
    if "x-coordinate" in row[i][0].split(","):
        continue
    else:
        column = row[i][0].split(",")
        second={}
        second["name"]=column[1]+"  "+column[2]
        second["size"]=column[2]
        data[column[0]].append(second)

clusterList = []
i=0
for elem in data.keys():
    first={}
    first["name"]="cluster "+str(i)
    first["children"]=data[elem]
    clusterList.append(first)
    i+=1


print json.dumps(clusterList, sort_keys=True, indent=4, separators=(',', ': '))

clusterStruct = {"name":"clusters", "children":clusterList}
with open("circle.json", "w") as f:             #Pass the json file as input to circle-packing.html
    f.write(json.dumps(clusterStruct, sort_keys=True, indent=4, separators=(',', ': ')))
