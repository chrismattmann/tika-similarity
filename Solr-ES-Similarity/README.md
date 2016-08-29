
# Flask based REST application for Solr Elasticsearch similarity using Jaccard, Edit-distance, Cosine & K-means metrics

Persists data onto a Document Store, which is later Clustered & Visualized in D3

1.Mount your raw images & Start Solr Instance

```
cd /path/to/images/directory/
python -m SimpleHTTPServer
```

2.Source the below Env Variable
```
export IMAGE_MOUNT=http://localhost:8000/
```

3.Start the Flask application
```
cd /path/to/Solr-ES-Similarity
python solr-similarity.py
```


4.Open the concerning D3 Viz REST endpoints in your browser

####Jaccard Metadata Key
http://localhost:5000/static/dynamic-cluster.html

####Jaccard Metadata Value
http://localhost:5000/static/dynamic-cluster-value.html

####k-means
http://localhost:5000/static/dynamic-cluster-kmeans.html


###Thresholding

**Try** to cluster pairwise similarity scores (based on Jaccard(wrt Golden Feature Set), Edit, Cosine distance)
by setting a threshold value

Number of clusters that will be found is Not known Apriori

Applicable D3 Viz = dynamic cluster, circlepacking


###Clustering

Using a metadata feature, such as string length, Cluster documents represented in N dimensional feature space as Vectors
using Euclidean distance.

Specify the number of clusters to find Apriori

1.**k-means clustering for absolute distance scores**

Applicable D3 Viz = dynamic cluster

2.**shared Nearest Neigbor clustering for pairwise similarity scores**

Applicable D3 Viz = dynamic cluster, circlepacking with tooltips