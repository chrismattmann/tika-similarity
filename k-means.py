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
import argparse, os, csv, itertools

maxFeatureLen = {}

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
    for feature in maxFeatureLen:

        dimension_sum = 0.0
        for point in list_of_points:
            try:
                dimension_sum += point.features[feature]
            except KeyError:
                continue                
        new_centroid.features[feature] = float(dimension_sum)/len(list_of_points)

    return new_centroid


def initializeCentroids(list_of_points, list_of_centroids):
    
    #get all keys

    '''
    pick 3 random points, & remove them from dataset, & cluster around those points
    less computationally intensive
    '''
    
    union_features = set()
    for point in list_of_points:
        union_features |= set(point.features.keys())

    #get max length of each Key

    #for key in union_features:
    
    for point in list_of_points:
        for key in point.features:
            try:
                if point.features[key] > maxFeatureLen[key]:                    
                    maxFeatureLen[key] = point.features[key]

            except KeyError:
                maxFeatureLen[key] = point.features[key]


    for centroid in list_of_centroids:
        
        for key in maxFeatureLen:
            centroid.features[key] = randint(0, maxFeatureLen[key])


    return list_of_centroids


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


def K_Means(inputDir, acceptTypes, no_centroids):

    list_of_points = []
    centroids = []

    for eachFile in filterFiles(inputDir, acceptTypes):
        list_of_points.append(Vector(parser.from_file(eachFile)["metadata"]))

    for i in range(no_centroids):
        centroids.append(Vector())

    centroids = initializeCentroids(list_of_points, centroids)
        

    #centroids.append(Vector(randVect))


    # perform iterations till convergence    # default 300

    #print centroids[0].features

    #print list_of_points[0].features

    #print list_of_points[0].euclidean_dist(centroids[0])

    
    clusters = cluster_assignment(list_of_points, centroids)

    old_clusters = None

    # generates different clusters each time
    # leverage the same "Dongni" compute-clusters.py
    for i in range(0, 300):

        new_centroids =  move_centroid(clusters)

        #old_clusters = clusters

        clusters = cluster_assignment(list_of_points, new_centroids)


    print clusters
    #old_centroids = None

    #old_clusters = first_clusters   

        
        




    

    #return cost coefficent



if __name__ == "__main__":

    argParser = argparse.ArgumentParser('K means Clustering')
    argParser.add_argument('--inputDir', required=True, help='path to directory containing files')
    #argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing k-means cluster assignments')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    if args.inputDir:# and :

        K_Means(args.inputDir, args.accept, 3)

        #compute k-means from k=1 to k=10 and get cost function
        #k =1 to k=10 cluster centroids

        #get max in each dimentsion of each vector 

        # run it for same value of k multiple times
        # different values of k 