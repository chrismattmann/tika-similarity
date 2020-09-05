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

import numpy as np
import sklearn.cluster
import os, editdistance, itertools, argparse, csv
import json
from vector import Vector
from tika import parser
from functools import reduce

'''This script uses sklearns Affinity propogation module to cluster based on different precomputed distance metrics
Affinity Propogation : http://www.sciencemag.org/content/315/5814/972.short
'''

#converts input attribute to string representation
def stringify(attribute_value):
    if isinstance(attribute_value, list):
        return str((", ".join(attribute_value)).encode('utf-8').strip())
    else:
        return str(attribute_value.encode('utf-8').strip())

#find edit distance between input attributes, config_params read from config file to pick only attributes mentioned in the config file
def findeditdistance(feature1,feature2,config_params):
    # print(feature1)
    intersect_features = set(feature1.keys()) & set(feature2.keys())

    if(config_params):
        intersect_features = [feature for feature in intersect_features if feature in config_params ]
    else:
        intersect_features = [feature for feature in intersect_features if feature != "resourceName" ]

    record_edit_distance = 0.0
    for feature in intersect_features:
        record1_feature_value = stringify(feature1[feature])
        record2_feature_value = stringify(feature2[feature])

        if len(record1_feature_value) == 0 and len(record2_feature_value) == 0:
            feature_distance = 0.0
        else:
            feature_distance = float(editdistance.eval(record1_feature_value, record2_feature_value))/(len(record1_feature_value) if len(record1_feature_value) > len(record2_feature_value) else len(record2_feature_value))

        record_edit_distance += feature_distance

    record_edit_distance /= float(len(intersect_features))    #average edit distance

    return record_edit_distance


#find jaccards distance between input attributes, config_params read from config file to pick only attributes mentioned in the config file
def jaccardsdistance(feature1,feature2,config_params):
    
    if(config_params):
        isCoExistant = lambda k: ( k in feature2 and k in (config_params)) and ( feature1[k] == feature2[k] )
    else:
        config_params=["resourceName"]
        isCoExistant = lambda k: ( k in feature2 and k in (config_params)) and ( feature1[k] == feature2[k] )
    intersection = reduce(lambda m,k: (m + 1) if isCoExistant(k) else m, list(feature1.keys()), 0)

    union = len(list(config_params.keys())) + len(list(config_params.keys())) - intersection
    jaccard = float(intersection) / union
    return jaccard

#find cosine distance between input attributes, config_params read from config file to pick only attributes mentioned in the config file
def cosinedistance(feature1,feature2,config_params):
    v1 = Vector(feature1['id'], feature1,config_params)
    v2 = Vector(feature2['id'], feature2,config_params)
    return v1.cosTheta(v2)

#convert input dict to unicode
def convertUnicode( fileDict ) :
    fileUTFDict = {}
    for key in fileDict:
        if isinstance(key, str) :
            key = key.encode('utf-8').strip()
        value = fileDict.get(key)
        if isinstance(value, str) :
            value = value.encode('utf-8').strip()
        fileUTFDict[key] = value

    return str(fileUTFDict)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser('Edit Distance, Jaccards and Cosine Similarity using Affinity Networks')
    argParser.add_argument('--inputFile', required=False, help='input JSON file')
    argParser.add_argument('--distance', required=True, help='distance metric to use. values: editdistance,jaccards,cosine')
    argParser.add_argument('--config', required=False, help='optional : fields to consider to calculate distance, by default all fields will be included. Format key:[datatye]')
    argParser.add_argument('--jsonKey', required=False, help='optional : JSON file key to load data from')
    argParser.add_argument('--inputDir',required=False,help='path to directory containing files')
    argParser.add_argument('--uniqueId',required=True,help='unique id to recognise individual documents')

    args = argParser.parse_args()

    config_params={}
    if(args.inputDir):
        filename_list = []
        for root, dirnames, files in os.walk(args.inputDir):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for filename in files:
                if not filename.startswith('.'):
                    filename_list.append(os.path.join(root, filename))
        try:
            #storing metadata(dict/json) of all files in filename_list which is used to calculate distance metric
            jsonObjsList = [parser.from_file(filename)["metadata"] for filename in filename_list if "metadata" in parser.from_file(filename)]
            jsonObjsList=np.asarray(jsonObjsList)
        except ConnectionError:
            sleep(1)
    else:
        inputFile=open(args.inputFile)
        if(args.jsonKey):
            jsonObjsList=json.load(inputFile)[args.jsonKey]
        else:
            jsonObjsList=json.load(inputFile)
        jsonObjsList=np.asarray(jsonObjsList)

#parsing config file
        if(args.config):
            config_file=open(args.config)
            for line in config_file:
                line=line.rstrip()
                fields=line.split(":")
                if(len(fields)>1):
                    config_params[fields[0]]=fields[1]
                else:
                    config_params[fields[0]]='string'
            
#call different distance metric based on input
    if(args.distance=='editdistance'):
        similarity = -1*np.array([[findeditdistance(record1,record2,config_params) for record1 in jsonObjsList] for record2 in jsonObjsList])

    if(args.distance=='jaccards'):
        similarity = -1*np.array([[jaccardsdistance(record1,record2,config_params) for record1 in jsonObjsList] for record2 in jsonObjsList])

    if(args.distance=='cosine'):
        similarity= -1*np.array([[cosinedistance(record1,record2,config_params) for record1 in jsonObjsList] for record2 in jsonObjsList])

#Affinity Propogation for clustering
    affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
    affprop.fit(similarity)

#root,curr_parent,child are used to format data according to clusters.json which can be visualised using D3(cluster-d3.html/dynamic-cluster.html)
    root={"name":"clusters","children":[]}
    for cluster_id in np.unique(affprop.labels_):
        exemplar = jsonObjsList[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(jsonObjsList[np.nonzero(affprop.labels_==cluster_id)])

        curr_parent={"children":[],"name":cluster_id}
        for node in cluster:
            child={}
            # print(node)
            child["metadata"]=convertUnicode(node)
            #unique id should be present in the input document if similarity is run on JSON input if the script is run on directories by default filename is used as uniq id
            if(args.uniqueId in node):
                child["name"]=node[args.uniqueId]
                child["score"]=node[args.uniqueId]
            else:
                child["name"]=""
                child["score"]=""
            child["path"]=exemplar
            
            curr_parent["children"].append(child)
        root["children"].append(curr_parent)
    with open("clusters.json", "w") as f:
        f.write(json.dumps(root, sort_keys=True, indent=4, separators=(',', ': ')))



