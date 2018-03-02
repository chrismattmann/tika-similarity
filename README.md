[Apache Tika](http://tika.apache.org/) File Similarity based on Jaccard distance, Edit distance & Cosine distance
===

This project demonstrates using the [Tika-Python](http://github.com/chrismattmann/tika-python) package (Python port of Apache Tika) to compute file similarity based on Metadata features.

The script can iterate over all files in the current directory or given files by command line and derives their metadata features, then computes the union of all features. The union of all features become the "golden feature set" that all document features are compared to via intersect. The length of that intersect per file divided by the length of the unioned set becomes the similarity score.

Scores are sorted in reverse (descending) order which can be shown in three different Data-Driven document visualizaions. A companion project to this effort is [Auto Extractor](https://github.com/USCDataScience/autoextractor/wiki/Clustering-Tutorial) which uses [Apache Spark](http://spark.apache.org/) and [Apache Nutch](http://nutch.apache.org/) to take web crawl data, and produce D3-visualizations and clusters of similar pages.

Pre-requisite
===
0. Install [Tika-Python](http://github.com/chrismattmann/tika-python)

Installation
===
```
pip install editdistance
git clone https://github.com/chrismattmann/tika-img-similarity
```
You can also check out [ETLlib](https://github.com/chrismattmann/etllib/tree/master/etl/imagesimilarity.py)

How to use
===

Optional: Compute similarity only on specific IANA MIME Type(s) inside a directory using **--accept**

Key-based comparison
--------------------
This compares metadata feature names as a golden feature set
```
#!/usr/bin/env python2.7
python similarity.py -f [directory of files] [--accept [jpeg pdf etc...]]
or 
python similarity.py -c [file1 file2 file3 ...]
```
Value-based comparison
----------------------
This compares metadata feature names together with its value as a golden feature set
```
#!/usr/bin/env python2.7
python value-similarity.py -f [directory of files] [--accept [jpeg pdf etc...]]
or 
python value-similarity.py -c [file1 file2 file3 ...]
```

Edit Distance comparison on Metadata Values
-------------------------------------------
- This computes pairwise similarity scores based on Edit Distance Similarity.
- **Similarity Score of 1 implies an identical pair of documents.**

```
#!/usr/bin/env python2.7
python edit-value-similarity.py [-h] --inputDir INPUTDIR --outCSV OUTCSV [--accept [png pdf etc...]] [--allKeys]

--inputDir INPUTDIR  path to directory containing files

--outCSV OUTCSV      path to directory for storing the output CSV File, containing pair-wise Similarity Scores based on Edit distance

--accept [ACCEPT]    Optional: compute similarity only on specified IANA MIME Type(s)

--allKeys            Optional: compute edit distance across all metadata keys of 2 documents, else default to only intersection of metadata keys

```
```
Eg: python edit-value-similarity.py --inputDir /path/to/files --outCSV /path/to/output.csv --accept png pdf gif
```

Cosine Distance comparison on Metadata Values
---------------------------------------------
- This computes pairwise similarity scores based on Cosine Distance Similarity.
- **Similarity Score of 1 implies an identical pair of documents.**

```
#!/usr/bin/env python2.7
python cosine_similarity.py [-h] --inputDir INPUTDIR --outCSV OUTCSV [--accept [png pdf etc...]]

--inputDir INPUTDIR  path to directory containing files

--outCSV OUTCSV      path to directory for storing the output CSV File, containing pair-wise Similarity Scores based on Cosine distance

--accept [ACCEPT]    Optional: compute similarity only on specified IANA MIME Type(s)

```

Similarity based on Stylistic/Authorship features
-------------------------------------------------
- This calculates pairwise cosine similarity on bag of signatures/features produced by extracting stylistic/authorship features from text.

```
#!/usr/bin/env python2.7
python psykey.py --inputDir INPUTDIR --outCSV OUTCSV --wordlists WRODLIST_FOLDER

--inputDir INPUTDIR  path to directory containing files

--outCSV OUTCSV      path to directory for storing the output CSV File, containing pair-wise Similarity Scores based on Cosine distance of stylistic and authorship features

--wordlists WRODLIST_FOLDER    path to the folder that contains files that are word list belonging to different classes. eg Use the wordlist folder provided with the tika-similarity library. If adding your own, make sure that the file is .txt with one word per line. Also, the name of the file will be considered the name of the class.

```

Metalevenshtein string distance
-------------------------------
- This calculates Metalevenshtein (Inspired by the paper : Robust Similarity Measures for Named Entities Matching by Erwan et al.) distance between two strings.

```
#!/usr/bin/env python2.7

Usage:

import metalevenshtein as metalev
print metalev.meta_levenshtein('abacus1cat','cat1cus')


To use all the argument options in this function:

def meta_levenshtein(string1,string2,Sim='levenshtein',theta=0.5,strict=-1,idf=dict()):

    Implements ideas from the paper : Robust Similarity Measures for Named Entities Matching by Erwan et al.
    Sim = jaro_winkler, levenshtein : can be chosen as the secondary matching function.
    theta is the secondary similarity threshold: If set higher it will be more difficult for the strings to match.
    strict=-1 for doing all permutations of the substrings
    strict=1 for no permutations
    idf=provide a dictionary for {string(word),float(idf od the word)}: More useful when mathings multi word entities (And word importances are very important)
    like: 'harry potter', 'the wizard harry potter'

```

Bell Curve fitting and overlap
------------------------------
- Fits two datasets into bel curves and finds the area of overlap between the bell curves.


```
#!/usr/bin/env python2.7
import features as feat
data1=[1,2,3,3,2,1]
data2=[4,5,6,6,5,4]
area,error=feat.gaussian_overlap(data1,data2)
print area

```



D3 visualization
----------------

### Cluster viz 
- Jaccard Similarity
```
* python cluster-scores.py [-t threshold_value] (for generating cluster viz)
* open cluster-d3.html(or dynamic-cluster.html for interactive viz) in your browser
```
- Edit Distance & Cosine Similarity  
```
* python edit-cosine-cluster.py --inputCSV <PATH TO CSV FILE> --cluster <INTEGER OPTION> (for generating cluster viz)

  <PATH TO CSV FILE> - Path to CSV file generated by running edit-value-similarity.py or cosine_similarity.py
  <INTEGER OPTION> - Pass 0 to cluster based on x-coordinate, 1 to cluster based on y-coordinate, 2 to cluster based on similarity score

* open cluster-d3.html(or dynamic-cluster.html for interactive viz) in your browser
```

Default **threshold** value is 0.01.

<img src="https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/cluster.png" width = "200px" height = "200px" style = "float:left">
<img src="https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/interactive-cluster.png" width = "200px" height = "200px" style = "float:right">

### Circlepacking viz
- Jaccard Similarity
```
* python circle-packing.py (for generating circlepacking viz)
* open circlepacking.html(or dynamic-circlepacking.html for interactive viz) in your browser
```
- Edit Distance & Cosine Similarity  
```
* python edit-cosine-circle-packing.py --inputCSV <PATH TO CSV FILE> --cluster <INTEGER OPTION> (for generating circlepacking viz)

  <PATH TO CSV FILE> - Path to CSV file generated by running edit-value-similarity.py or cosine_similarity.py
  <INTEGER OPTION> - Pass 0 to cluster based on x-coordinate, 1 to cluster based on y-coordinate, 2 to cluster based on similarity score


* open circlepacking.html(or dynamic-circlepacking.html for interactive viz) in your browser
```
<img src="https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/circlepacking.png" width = "200px" height = "200px" style = "float:left">
<img src="https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/interactive-circlepacking.png" width = "200px" height = "200px" style = "float:right">

### Composite viz
This is a combination of cluster viz and circle packing viz.
The deeper color, the more the same attributes in the cluster.
```
* open compositeViz.html in your browser
```
![Image of composite viz](https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/composite.png)

### Sunburst viz
Visualization of clustering from Jaccard Similarity result
```
* python sunburst.py (for generating circlepacking viz)
* open sunburst.html
```
![Image of sunburst viz](https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/sunburst.png)

### Big data way
if you are dealing with big data, you can use it this way:
```
* python generateLevelCluster.py (for generating level cluster viz)
* open levelCluster-d3.html in your browser
```
You can set max number for each node **_maxNumNode**(default _maxNumNode = 10) in generateLevelCluster.py
![Image of level composite viz](https://github.com/dongnizh/tika-img-similarity/blob/refactor/snapshots/level-composite.png)

Questions, comments?
===================
Send them to [Chris A. Mattmann](mailto:chris.a.mattmann@jpl.nasa.gov).

Contributors
============
* Chris A. Mattmann, JPL
* Dongni Zhao, USC
* Harshavardhan Manjunatha, USC
* Thamme Gowda, USC
* Ayberk Yılmaz, USC
* Aravind Ram, USC
* Aishwarya Parameshwaran, USC
* Rashmi Nalwad, USC
* Asitang Mishra, JPL
* Suzanne Stathatos, JPL

License
===

This project is licensed under the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).







