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

_maxNumNode = 10

def main(argv = None) : 
	with open('clusters.json') as data_file:
		data = json.load(data_file)
		numOfCluster = len(data["children"])

		for i in range(0, numOfCluster):
			numOfPic = len(data["children"][i]["children"])
			if numOfPic > _maxNumNode:
				level = levelNum(data["children"][i]["children"])
				for j in range(1, level) : 
					clusterChildren = generateLevel(data["children"][i]["children"])
					data["children"][i]["children"] = clusterChildren
	with open("levelCluster.json", "w") as f:
		f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))



def levelNum(data, level = 1):
	cluster = {}
	numOfChildren = len(data)
	while numOfChildren / _maxNumNode>0:
		numOfChildren = numOfChildren / _maxNumNode
		level = level+1

	return level

def generateLevel(data):
	clusters = []
	numOfChildren = len(data)
	numOfGroup = numOfChildren / _maxNumNode
	for i in range(0, numOfGroup+1) :
		clusterData = []
		clusterGroupData ={}
		for j in range(_maxNumNode*i, min(_maxNumNode*(i+1), numOfChildren)):
			clusterData.append(data[j])
		clusterGroupData = {"name" : "group"+str(i), "children": clusterData}
		clusters.append(clusterGroupData)
	return clusters


if __name__ == "__main__" :
	sys.exit(main())
