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
from elasticsearch import Elasticsearch
from flask import Flask
import requests

app = Flask(__name__)
index = "example1"
_type = "polar"

# resp = es.get(index="example1", doc_type="polar", id="file:/Users/hmanjuna/Pictures/onlyJPG/0508_cold_thumb.jpg")




@app.route('/jaccard_KeyBased')     #decorator => URL endpoint for App
def jaccardAbsolute():

    es = Elasticsearch()

    #query = "http://localhost:9200/{0}/{1}/_search/?size=1000".format(index, _type)

    #resp = requests.get(query)

    res = es.search(index="example1", body={"query": {"match_all": {}}})

    #if resp.status_code == 200:

    return res['hits']['hits']






    #return resp.json()


    #resp = resp.text.replace("false", "False").replace("null", 'None')



    #return eval(resp)

        # print resp["_source"]


    #return json_response_d3







if __name__ == "__main__":
    app.run(debug=True)

