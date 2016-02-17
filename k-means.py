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
from vector import Vector
from random import randint
import argparse, os, csv, itertools, copy, json, sys

union_features = set()

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    filename_list = [filename for filename in filename_list if parser.from_file(filename)]
    if acceptTypes:
        filename_list = [filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8')).split('/')[-1] in acceptTypes]
    else:
        print "Accepting all MIME Types....."

    return filename_list


def compute_Mean(list_of_points):    

    new_centroid = Vector()
    for feature in union_features:

        dimension_sum = 0.0
        for point in list_of_points:
            try:
                dimension_sum += point.features[feature]
            except KeyError:
                continue                
        new_centroid.features[feature] = float(dimension_sum)/len(list_of_points)

    return new_centroid


def cluster_assignment(list_of_points, centroids):
    '''
    Assign points to nearest centroid 
    '''
    clusters = {}
    for point in list_of_points:

        distances = []
        for centroid in centroids:
            distances.append(point.euclidean_dist(centroid))

        try:
            clusters[distances.index(min(distances))].append(point)
        except KeyError:
            clusters[distances.index(min(distances))] = []
            clusters[distances.index(min(distances))].append(point)
                 
    return clusters


def move_centroid(clusters):
    '''
    Shift centroid to mean of assigned points
    '''
    new_centroids = []
    for key in clusters:
        new_centroids.append(compute_Mean(clusters[key]))

    return new_centroids


def K_Means(list_of_points, no_centroids):
    
    centroids = []

    for i in range(no_centroids):
        centroids.append(Vector())

    for centroid in centroids:
        random_point = list_of_points[randint(0, (len(list_of_points)-1) )]

        centroid.features = copy.deepcopy(random_point.features)
    

    # perform iterations till convergence    # default 300

    #print centroids[0].features    #print list_of_points[0].features    #print list_of_points[0].euclidean_dist(centroids[0])

    
    clusters = cluster_assignment(list_of_points, centroids)

    # generates different clusters each time
    # leverage the same "Dongni" compute-clusters.py
    for i in range(0, 300):

        new_centroids =  move_centroid(clusters)     #'''centroids vs new_centroids, use centroids again???'''

        clusters = cluster_assignment(list_of_points, new_centroids)   #''' #old_clusters = first_clusters '''

    ''' pseudocode 
    # clusters =>   converged / recent values of clusters???
    # new_centroids => recent value of c
    '''
    #print clusters

    # compute & return distortion (new_centroids, clusters)

    distortion_sum = 0.0
    for key in clusters:
        for point in clusters[key]:
            distortion_sum += point.euclidean_dist(new_centroids[key])
    distortion = distortion_sum / float(len(list_of_points))

    return [distortion, clusters]
    



if __name__ == "__main__":

    argParser = argparse.ArgumentParser('K-means Clustering of metadata values')
    argParser.add_argument('--inputDir', required=True, help='path to directory containing files')
    #argParser.add_argument('--outJSON', required=True, help='path to directory for storing the output CSV File, containing k-means cluster assignments')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    if args.inputDir:# and args.outCSV:

        list_of_points = []
        for eachFile in filterFiles(args.inputDir, args.accept):
            list_of_points.append(Vector(eachFile, parser.from_file(eachFile)["metadata"]))
        
        for point in list_of_points:
            union_features |= set(point.features.keys())

        print list_of_points[0].filename

        #global_minimas = []

        #for k in range(2, 10):

        global_minima = K_Means(list_of_points, 3)

        for i in range(0, 100):
            iteration = K_Means(list_of_points, 3)

            if iteration[0] < global_minima[0]:
                global_minima = iteration

        print global_minima

        with open("clusters.json", "w") as jsonF:

            json_data = {}

            cluster = []
            for key in global_minima[1]:    #clusters

                cluster_Dict = {}
                children = []
                for point in global_minima[1][key]:

                    node = {}
                    node["metadata"] = parser.from_file(point.filename)
                    node["name"] = point.filename.split('/')[-1]
                    node["path"] = point.filename                    
                    children.append(node)
                
                cluster_Dict["children"] = children
                cluster_Dict["name"] = "cluster" + str(key)

                cluster.append(cluster_Dict)

            json_file["children"] = cluster
            json_file["name"] = "clusters"

        
            json.dump(json_data, jsonF)





        #compute k-means from k=1 to k=10 and get cost function
        #k =1 to k=10 cluster centroids

        #get max in each dimentsion of each vector 

        # run it for same value of k multiple times
        # different values of k 

        '''
        if k-means found no clusters, remove that cluster id
        => at iteration 1
        or at the end of all iterations??
        '''