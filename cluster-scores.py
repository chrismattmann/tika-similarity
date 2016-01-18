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

try:
    import simplejson as json
except ImportError:
    import json

import sys

default_threshold = 0.01

usage = "Usage: python cluster-scores.py [-t threshold_value]"

def main(threshold):
    with open("similarity-scores.txt") as f:
        prior = None
        clusters = []
        clusterCount = 0
        cluster = {"name":"cluster"+str(clusterCount)}
        clusterData = []
        for line in f:
            if line.find("{") != -1:
                featureDataList = line.split(",",3) # file name,score,metadata
            else :
                featureDataList = line.split(",", 2)

            if not (len(featureDataList) == 3 or len(featureDataList) == 4):
                continue


            if prior != None:
                diff = prior-float(featureDataList[1])
            else:
                diff = -1.0

            # cleanse the \n
            featureDataList[1] = featureDataList[1].strip()
            if(len(featureDataList) == 4):
                featureData = {"name":featureDataList[0], "score":float(featureDataList[1]), "path" :featureDataList[2],  "metadata" : featureDataList[3]}
            elif (len(featureDataList) == 3):
                featureData = {"name":featureDataList[0], "score":float(featureDataList[1]), "path" :featureDataList[2]}

            if diff > threshold:
                cluster["children"] = clusterData
                clusters.append(cluster)
                clusterCount = clusterCount + 1
                cluster = {"name":"cluster"+str(clusterCount)}
                clusterData = []
                clusterData.append(featureData)
                prior = float(featureDataList[1])
            else:
                clusterData.append(featureData)
                prior = float(featureDataList[1])

        #add the last cluster into clusters
        cluster["children"] = clusterData
        clusters.append(cluster)
        clusterCount = clusterCount + 1
        cluster = {"name":"cluster"+str(clusterCount)}

    clusterStruct = {"name":"clusters", "children":clusters}
    with open("clusters.json", "w") as f:
        f.write(json.dumps(clusterStruct, sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    threshold = default_threshold
    if len(sys.argv) == 3 and sys.argv[1] == "-t":
        try:
            threshold = float(sys.argv[2])
        except:
            print usage
            print "Using default threshold value..."

    main(threshold)
