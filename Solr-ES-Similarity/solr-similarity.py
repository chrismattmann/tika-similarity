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

from solr import Solr
from flask import Flask
import pandas as pd
from vector import Vector
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import requests, json, os, operator

app = Flask(__name__)

def featurizeDoc(doc):
    """
        get key : value of metadata
    """
    doc_features = []
    for key in doc:
        doc_features.append("{0}: {1}".format(key, doc[key]))
    return doc_features


def computeJaccardValue(solrInstance):

    union_feature_values = set()
    docs = solrInstance.query_iterator(query="*:*", start=0)
    for doc in docs:
        union_feature_values |= set(featurizeDoc(doc))


    total_num_features = len(union_feature_values)
    docs = solrInstance.query_iterator(query="*:*", start=0)
    bufferDocs = []
    for doc in docs:

        overlap =  set(featurizeDoc(doc)) & union_feature_values
        doc["jaccard_value_abs"] = float(len(overlap)) / total_num_features

        bufferDocs.append(doc)

    bufferDocs.sort(key=operator.itemgetter('jaccard_value_abs'), reverse=True)

    return bufferDocs


def computeJaccardMeta(solrURL, solrInstance):

    lukeURL = "http://{0}/admin/luke?numTerms=0&wt=json".format(solrURL.split("://")[-1].rstrip('/'))
    luke = requests.get(lukeURL)

    #if not luke: return "<h1>Check if Solr server is up</h1>"
    if luke.status_code == 200:
        luke = luke.json()
        union_feature_names = set(luke["fields"].keys())
        total_num_features = len(union_feature_names)

        docs = solrInstance.query_iterator(query="*:*", start=0)

        bufferDocs = []
        for doc in docs:
            overlap = set(doc.keys()) & set(union_feature_names)
            # not performing atomic update to Solr index, just computing scores & clustering
            # no need to map to solr dynamic field
            doc["jaccard_meta_abs"] = float(len(overlap)) / total_num_features

            bufferDocs.append(doc) #yield doc

        bufferDocs.sort(key=operator.itemgetter('jaccard_meta_abs'), reverse=True)
        return bufferDocs

    # perform atomic updates,
    # query Solr with sort="metadataScore" in kwargs payload


# hit the REST endpoint to choose your distance metric
@app.route('/<string:core>/threshold/jaccard/<string:metric>/<float:threshold>')
def jaccard(core, metric, threshold=0.01):

    solrURL = "http://localhost:8983/solr/" + core
    solrInstance = Solr(solrURL)

    if metric == "meta":
        docs = computeJaccardMeta(solrURL, solrInstance)
    elif metric == "value":
        docs = computeJaccardValue(solrInstance)

    json_data = {"name": "clusters", "children": []}

    prior_node = { "metadata": json.dumps(docs[0]),
                   "name": docs[0]['id'].split('/')[-1],
                    "path": os.environ["IMAGE_MOUNT"] + docs[0]['id'].split('/')[-1].split('.')[0] + ".jpg",
                    "score": docs[0]["jaccard_{0}_abs".format(metric)]
    }

    prior = docs[0]["jaccard_{0}_abs".format(metric)]

    cluster0 = { "name": "cluster0",
                 "children": [prior_node]
    }

    clusters = [cluster0]
    clusterCount = 0

    for i in range(1, len(docs)):

        node = { "metadata": json.dumps(docs[i]),
                 "name": docs[i]['id'].split('/')[-1],
                 "path": os.environ["IMAGE_MOUNT"] + docs[i]['id'].split('/')[-1].split('.')[0] + ".jpg",
                 "score": docs[i]["jaccard_{0}_abs".format(metric)]
        }

        diff = prior - docs[i]["jaccard_{0}_abs".format(metric)]

        if diff <= threshold:
            clusters[clusterCount]["children"].append(node)
        else:
            clusterCount += 1
            newCluster = { "name": "cluster"+str(clusterCount),
                           "children": [node]
            }
            clusters.append(newCluster)

        prior = docs[i]["jaccard_{0}_abs".format(metric)]

    json_data["children"] = clusters

    return json.dumps(json_data)


@app.route('/<string:core>/cluster/kmeans/') #<int:kval>
def sk_kmeans(core): #, kval=3

    solrURL = "http://localhost:8983/solr/" + core
    solrInstance = Solr(solrURL)

    list_of_points = []
    docs = solrInstance.query_iterator(query="*:*", start=0)

    for doc in docs:
        list_of_points.append(Vector(doc['id'], doc))

    list_of_Dicts = (point.features for point in list_of_points)

    df = pd.DataFrame(list_of_Dicts)
    df = df.fillna(0)

    silhouettes = {}
    for k in range(2, 10):

        kmeans = KMeans(n_clusters=k,
                    init='k-means++',
                    max_iter=300,  # k-means convergence
                    n_init=10,  # find global minima
                    n_jobs=-2,  # parallelize
                    )

        labels = kmeans.fit_predict(df)
        silhouettes[k] = silhouette_score(df, labels)


    return str(silhouettes)



if __name__ == "__main__":
    app.run(debug=True)



    #keep tab on docID when iterating through Solr response