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

import tika
import os
tika.initVM()
from tika import parser
import operator

union_feature_names = set()
file_parsed_data = {}
resemblance_scores={}

for filename in os.listdir("."):
    if not os.path.isfile(filename) or not ".jpg" in filename:
        continue

    # first compute the union of all features
    parsedData = parser.from_file(filename)
    file_parsed_data[filename] = parsedData["metadata"]
    union_feature_names = union_feature_names | set(parsedData["metadata"].keys())

total_num_features = len(union_feature_names)

# now compute the specific resemblance and containment scores
for filename in file_parsed_data.keys():
    overlap = {}
    overlap = set(file_parsed_data[filename].keys()) & set(union_feature_names) 
    resemblance_scores[filename] = float(len(overlap))/total_num_features

sorted_resemblance_scores = sorted(resemblance_scores.items(), key=operator.itemgetter(1), reverse=True)

print "Resemblance:\n"
for tuple in sorted_resemblance_scores:
    print tuple[0]+","+str(tuple[1])
