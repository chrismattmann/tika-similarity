[Apache Tika](http://tika.apache.org/) Jaccard Based Image Similarity
===

This project demonstrates using the [Tika-Python](http://github.com/chrismattmann/tika-python) package (Python port of Apache Tika) to compute Image similarity based on Metadata features.

The script can iterate over all images in the current directory or given images by command line and derives their metadata features, then computes the union of all features. The union of all features become the "golden feature set" that all image document features are compared to via intersect. The length of that intersect per image divided by the length of the unioned set becomes the similarity score.

Scores are sorted in reverse (descending) order which can be shown in three different Data-Driven document visualizaions.

Pre-requisite
===
0. `Install [Tika-Python](http://github.com/chrismattmann/tika-python)`

Installation
===
```
git clone https://github.com/chrismattmann/tika-img-similarity

```
You can also check out [ETLlib](https://github.com/chrismattmann/etllib)/etl/imagesimilarity.py

How to use
===

Key-based comparison
--------------------
This compares metadata feature names as a golden feature set
```
#!/usr/bin/env python2.7
python similarity.py -f [directory of images] or 
python similarity.py -c [file1 file2 file3 ...]

```
Value-based comparison
----------------------
This compares metadata feature names together with its value as a golden feature set
```
#!/usr/bin/env python2.7
python value-similarity.py -f [directory of images] or 
python value-similarity.py -c [file1 file2 file3 ...]

```

D3 visualization
----------------

### cluster viz 
```
* python cluster-scores.py (for generating cluster viz)
* open cluster-d3.html(or dynamic-cluster.html for interactive viz) in your browser

```

###circlepacking viz
```
* python circle-packing.py (for generating circlepacking viz)
* open circlepacking.html(or dynamic-circlepacking.html for interactive viz) in your browser

```

###composite viz
This is a combination of cluster viz and circle packing viz
```
* open compositeViz.html in your browser

```

###Big data method
if you are dealing with big data, you can use it this way:
```
* python generateLevelCluster.py (for generating level cluster viz)
* open levelCluster-d3.html in your browser

```

Questions, comments?
===================
Send them to [Chris A. Mattmann](mailto:chris.a.mattmann@jpl.nasa.gov).

License
===

This project is licensed under the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).







