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
from tika import parser
import pandas as pd
from vector import Vector
from sklearn.cluster import KMeans
import argparse, os, json


def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))
    
    filename_list = (filename for filename in filename_list if "metadata" in parser.from_file(filename))
    if acceptTypes:
        filename_list = (filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8').decode('utf-8')).split('/')[-1] in acceptTypes)
    else:
        print("Accepting all MIME Types.....")

    return filename_list


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('k-means Clustering of documents based on metadata values')
    argParser.add_argument('--inputDir', required=True, help='path to directory containing files')
    argParser.add_argument('--outJSON', required=True, help='/path/to/clusters.json containing k-means cluster assignments')
    argParser.add_argument('--Kvalue', help='number of clusters to find')
    #argParser.add_argument('--findK', action='store_true', help='find the optimal value of K')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    # cluster for a particular value of K
    # if args.inputDir and args.outJSON and args.findK:


    if args.inputDir and args.outJSON and args.Kvalue:

        list_of_points = []
        for eachFile in filterFiles(args.inputDir, args.accept):
            list_of_points.append(Vector(eachFile, parser.from_file(eachFile)["metadata"]))
        
        
        list_of_Dicts = (point.features for point in list_of_points)

        df = pd.DataFrame(list_of_Dicts)
        df = df.fillna(0)
        
        print(df.shape)

        kmeans = KMeans(n_clusters=int(args.Kvalue),
                        init='k-means++',
                        max_iter=300,   # k-means convergence
                        n_init=10,      # find global minima
                        n_jobs=-2,    # parallelize
                        )

        labels = kmeans.fit_predict(df)  # unsupervised (X, y=None)

        print(labels)    # kmeans.labels_

        clusters = {}
        for i in range(0, len(labels)):

            node = { "metadata": json.dumps(list_of_points[i].features),
                     "name": list_of_points[i].filename.split('/')[-1],
                     "path": list_of_points[i].filename
                     }
            try:
                clusters[str(labels[i])].append(node)
            except KeyError:
                clusters[str(labels[i])] = []
                clusters[str(labels[i])].append(node)


        # generate clusters.JSON
        with open(args.outJSON, "w") as jsonF:

            json_data = {"name": "clusters"}
            children = []

            for key in clusters:
                cluster_children = {"name": "cluster"+key, "children": clusters[key]}
                children.append(cluster_children)

            json_data["children"] = children
            json.dump(json_data, jsonF)


        # print matplotlib
        # user chooses k => generates k


        # find elbow

        #kmeans.transform()


        # String Length Of Course 
        # df.to_csv("bashhshs.csv", sep=',')
