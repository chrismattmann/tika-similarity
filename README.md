[Apache Tika](http://tika.apache.org/) Jaccard Based Image Similarity
===

This project demonstrates using the [Tika-Python](http://github.com/chrismattmann/tika-python)
package (Python port of Apache Tika) to compute Image similarity based on Metadata features.
The script currently iterates over all jpg images in the current directory and derives their
metadata feature names, and computes the union of all feature names. The union of all feature
names becomes the "golden feature set" that all image document features are compared to via
intersect. The length of that intersect per image divided by the length of the unioned set 
becomes the similarity score. Scores are sorted in reverse (descending) order and then output
in the sorted_scores array.

License
===

This project is licensed under the [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).


Use
===

Pre-requisite
===
0. Install [Tika-Python](http://github.com/chrismattmann/tika-python)

Using existing data
===
1. git clone https://github.com/chrismattmann/tika-img-similarity.git into
a folder that a web browser can see
2. pop open index.html in a browser

Using your own image data from crawl
===
0. mkdir -p $HOME/deploy && cd $HOME/deploy
1. git clone https://github.com/chrismattmann/tika-img-similarity.git into
a folder that a web browser can see
2. export PATH=$HOME/deploy/tika-img-similarity:${PATH}
3. cd /path/to/your/images
4. img_feature_similarity_tika.py > similarity-scores.txt
5. cluster_scores.py > clusters.json
6. mv clusters.json $HOME/deploy/tika-img-similarity/testdata
7. pop open index.html in a browser
8. #win
