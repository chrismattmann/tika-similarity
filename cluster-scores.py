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

threshold = 0.01
with open("img-clusters.txt") as f:
    prior = None
    clusters = []
    cluster = []
    for line in f:
        featureData = line.split(",") # file name,score
        if len(featureData) != 2:
            continue

        if prior != None:
            diff = prior-float(featureData[1])
        else:
            diff = -1.0

        # cleanse the \n
        featureData[1] = featureData[1].strip()

        if diff > threshold:
            clusters.append(cluster)
            cluster = []
            cluster.append(featureData)
            prior = float(featureData[1])
        else:
            cluster.append(featureData)
            prior = float(featureData[1])

print clusters

            
        
