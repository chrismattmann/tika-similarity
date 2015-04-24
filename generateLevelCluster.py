import json
import sys

__threshold = 10

def main(argv = None) : 
	with open('testdata/clusters5.json') as data_file:
		data = json.load(data_file)
		numOfCluster = len(data["children"])

		for i in range(0, numOfCluster):
			numOfPic = len(data["children"][i]["children"])
			if numOfPic > __threshold :
				level = levelNum(data["children"][i]["children"])
				for j in range(1, level) : 
					clusterChildren = generateLevel(data["children"][i]["children"])
					data["children"][i]["children"] = clusterChildren
	with open("levelCluster.json", "w") as f:
		f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))



def levelNum(data, level = 1):
	cluster = {}
	numOfChildren = len(data)
	while numOfChildren / __threshold >0:
		numOfChildren = numOfChildren / __threshold
		level = level+1

	return level

def generateLevel(data):
	clusters = []
	numOfChildren = len(data)
	numOfGroup = numOfChildren / __threshold
	for i in range(0, numOfGroup+1) :
		clusterData = []
		clusterGroupData ={}
		for j in range(__threshold*i, min(__threshold*(i+1), numOfChildren)):
			clusterData.append(data[j])
		clusterGroupData = {"name" : "group"+str(i), "children": clusterData}
		clusters.append(clusterGroupData)
	return clusters


if __name__ == "__main__" :
	sys.exit(main())