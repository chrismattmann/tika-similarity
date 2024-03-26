import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from collections import Counter

# Downloading the data from CSV file with passing on the first line
data = pd.read_csv('edit.csv', skiprows=1, names=['file1', 'file2', 'similarity_score'])

# Transforming the data to the format which is conviniet for processing
file_pairs = data[['file1', 'file2']].values
similarity_scores = data['similarity_score'].values.reshape(-1, 1)

# Creating clusters based on the similarity extent of files
n_clusters = 10  # quantity of clusters 
clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
clusters = clustering.fit_predict(similarity_scores)

# Counting the quantity of elements of transitions between clusters
transitions = Counter()
for i in range(len(clusters)):
    cluster1 = clusters[i]
    for j in range(i + 1, len(clusters)):
        cluster2 = clusters[j]
        if cluster1 != cluster2:
            transitions[(cluster1, cluster2)] += 1

# Writing the results into csv file
result_data = []
for (cluster1, cluster2), count in transitions.items():
    result_data.append([cluster1 + 1, cluster2 + 1, count])

result_df = pd.DataFrame(result_data, columns=['source', 'target', 'value'])
result_df.to_csv('edit_result.csv', index=False)
