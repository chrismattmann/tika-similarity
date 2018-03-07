import json
import sys
import ast


def main(argv = None):
    threshold = 0.01
    with open("similarity-scores.txt") as f:
        prior = None
        clusters = []
        clusterCount = 0
        cluster = {"name":"cluster"+str(clusterCount)}
        clusterData = []
        for line in f:
            if "Resemblance" in line:
                continue
            featureDataList = line.split("{", 1)
            metadata = '{' + featureDataList[1]
            featureDataList = featureDataList[0].rsplit(",", 3)
            featureDataList.remove('')
            featureDataList[2] = metadata

            if len(featureDataList) != 3:
                continue
            if prior != None:
                diff = prior-float(featureDataList[1])
            else:
                diff = -1.0

            # cleanse the \n
            featureDataList[1] = featureDataList[1].strip()
            #featureData = {"name":featureDataList[0], "score":float(featureDataList[1]), "metadata" : featureDataList[2]}

            if diff > threshold:
                cluster["children"] = treemap(clusterData)
                clusters.append(cluster)
                clusterCount = clusterCount + 1
                cluster = {"name":"cluster"+str(clusterCount)}
                clusterData = []
                clusterData.append(featureDataList[2])
                prior = float(featureDataList[1])
            else:
                clusterData.append(featureDataList[2])
                prior = float(featureDataList[1])

        #add the last cluster into clusters
        cluster["children"] = treemap(clusterData)
        clusters.append(cluster)
        clusterCount = clusterCount + 1
        cluster = {"name":"cluster"+str(clusterCount)}

    clusterStruct = {"name":"clusters", "children":clusters}
    with open("tree.json", "w") as f:
        f.write(json.dumps(clusterStruct, sort_keys=True, indent=4, separators=(',', ': ')))


def treemap( metadataLists) :
    metadataList = []
    treemaps = set()
    for line in metadataLists:
        metadata = ast.literal_eval(line)
        for item in metadata.keys():
            if item not in treemaps :
                treemaps.add(item)
                treemap = {}
                treemap["name"] = item
                treemap["size"] = 1
                metadataList.append(treemap)
            else :
                for value in metadataList:
                    if item  == value["name"]:
                        count = value["size"]
                        index = metadataList.index(value)
                        metadataList.remove(value)
                        treemap = {}
                        treemap["name"] = item
                        treemap["size"] = count +1
                        metadataList.insert(index, treemap)
    return metadataList

if __name__ == "__main__":
    sys.exit(main())


