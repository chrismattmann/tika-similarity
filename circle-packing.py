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
import ast


def main(argv = None):
    threshold = 0.01
    with open("similarity-scores.txt") as f:
        prior = None
        clusters = []
        clusterCount = 0
        cluster = {"name":"cluster"+str(clusterCount)}
        clusterData = []
        for line in f:
            if "Resemblance" in line:
                continue
            featureDataList = line.split("{", 1)
            metadata = '{' + featureDataList[1]
            featureDataList = featureDataList[0].rsplit(",", 3)
            featureDataList.remove('')
            featureDataList[2] = metadata

            if len(featureDataList) != 3:
                continue
            if prior != None:
                diff = prior-float(featureDataList[1])
            else:
                diff = -1.0

            # cleanse the \n
            featureDataList[1] = featureDataList[1].strip()
            #featureData = {"name":featureDataList[0], "score":float(featureDataList[1]), "metadata" : featureDataList[2]}

            if diff > threshold:
                cluster["children"] = circle(clusterData)
                clusters.append(cluster)
                clusterCount = clusterCount + 1
                cluster = {"name":"cluster"+str(clusterCount)}
                clusterData = []
                clusterData.append(featureDataList[2])
                prior = float(featureDataList[1])
            else:
                clusterData.append(featureDataList[2])
                prior = float(featureDataList[1])

        #add the last cluster into clusters
        cluster["children"] = circle(clusterData)
        clusters.append(cluster)
        clusterCount = clusterCount + 1
        cluster = {"name":"cluster"+str(clusterCount)}

    clusterStruct = {"name":"clusters", "children":clusters}
    with open("circle.json", "w") as f:
        f.write(json.dumps(clusterStruct, sort_keys=True, indent=4, separators=(',', ': ')))


def circle( metadataLists) : 
    metadataList = []
    circles = set()
    for line in metadataLists:
        metadata = ast.literal_eval(line)
        for item in metadata.keys():
            if item not in circles :
                circles.add(item)
                circle = {}
                circle["name"] = item
                circle["size"] = 1
                metadataList.append(circle)
            else :
                for value in metadataList:
                    if item  == value["name"]:
                        count = value["size"]
                        index = metadataList.index(value)
                        metadataList.remove(value)
                        circle = {}
                        circle["name"] = item
                        circle["size"] = count +1
                        metadataList.insert(index, circle)
    return metadataList

if __name__ == "__main__":
    sys.exit(main())


