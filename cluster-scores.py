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

threshold = 0.01
with open("similarity-scores.txt") as f:
    prior = None
    clusters = {}
    cluster = []
    clusterCount = 0
    for line in f:
        featureDataList = line.split(",") # file name,score
        if len(featureDataList) != 2:
            continue

        if prior != None:
            diff = prior-float(featureDataList[1])
        else:
            diff = -1.0

        # cleanse the \n
        featureDataList[1] = featureDataList[1].strip()
        featureData = {"name":featureDataList[0], "score":float(featureDataList[1])}

        if diff > threshold:
            clusters["cluster"+str(clusterCount)] = cluster
            clusterCount = clusterCount+1
            cluster = []
            cluster.append(featureData)
            prior = float(featureDataList[1])
        else:
            cluster.append(featureData)
            prior = float(featureDataList[1])

print json.dumps(clusters, sort_keys=True, indent=4, separators=(',', ': '))
            
        
