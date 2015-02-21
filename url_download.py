import urllib2
import json
import os
url = "http://nsfpolardata.dyndns.org:8983/solr/nasa_amd/select?q=*%3A*&fq=contentType%3Aimage%2Fjpeg&rows=20&wt=json&indent=true"
response = urllib2.urlopen(url).read()
with open('data.json', 'w') as f:
	f.write(response)
json_data = open('data.json', 'r')
data = json.load(json_data)
url_data = []
for record in data['response']['docs']:
	url_data.append(str(record['url']))
	name = os.path.basename(record['url'].rstrip(os.sep))
	image = urllib2.urlopen(record['url']).read()
	with open(name, 'w') as f:
		f.write(image)


