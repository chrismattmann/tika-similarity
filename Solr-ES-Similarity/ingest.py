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
from tika import parser
from solr import Solr
import argparse, os
import pandas as pd

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    filename_list = (filename for filename in filename_list if "metadata" in parser.from_file(filename))
    if acceptTypes:
        filename_list = (filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8')).split('/')[-1] in acceptTypes)
    else:
        print("Accepting all MIME Types.....")

    return filename_list


def stringify(attribute_value):
    if isinstance(attribute_value, list):
        return str((", ".join(attribute_value)).encode('utf-8').strip())
    elif isinstance(attribute_value, int) or isinstance(attribute_value, float):
        return str(attribute_value)
    else:
        return str(attribute_value.strip())


def lazySolr(inputDir, accept):

    for doc in filterFiles(inputDir, accept):
        parsed = parser.from_file(doc)

        document = { "id": "file:" + os.path.abspath(inputDir) + "/" + str(parsed["metadata"].pop("resourceName", None).encode("utf-8")),
                     "content": parsed["content"]
        }

        for key in parsed["metadata"]:
            mappedField = key + "_s_md"

            value = stringify(parsed["metadata"][key])
            if value:
                document[mappedField] = value

        yield document

def lazyDataset(dataset):

    df = pd.read_csv(dataset)
    df.drop(["NEF", "TIFF", "Keywords"], axis=1, inplace=True)
    df = df.fillna("")

    columns = list(df.columns)
    columns.remove("File")

    for index, row in df.iterrows():

        document = { "id": str(row["File"].encode("utf-8")) }

        for col in columns:
            mappedField = col + "_s_md"

            value = stringify(row[col])
            if value:
                document[mappedField] = value  # map & store metadata field in Solr

        yield document


def solrIngest(URL, dataset=None, inputDir=None, accept=None):

    solr = Solr(URL)
    documents = []

    if dataset:
        documents = lazyDataset(dataset)
    elif inputDir:
        documents = lazySolr(inputDir, accept)

    count, res = solr.post_iterator(documents, commit=True, buffer_size=100)

    print(("Res : %s; count=%d" % (res, count)))

if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Ingest Documents into Solr 4.10.4 or ES 2.3.1')
    argParser.add_argument('--URL', required=True, help='Solr or Elastic Document Store URL ## http://localhost:8983/solr/core1')
    argParser.add_argument('--inputDir', help='path to directory containing files')
    argParser.add_argument('--dataset', help="path to ingest RAISE or flickr EXIF file")
    argParser.add_argument('--accept', nargs='+', type=str, help='Ingest only certain IANA MIME types')
    args = argParser.parse_args()

    if args.dataset:
        solrIngest(args.URL, args.dataset)

    elif args.inputDir:
        if "solr" in args.URL:
            solrIngest(args.URL, "", args.inputDir, args.accept)
        else:
            print("Defaulting to Elasticsearch")
            #ingestES(args.URL, args.inputDir, args.accept)


"""
def ingestES(inputDir, accept):

    #intersect_features = set()
    # has to be done thru querying ES efficiently filter queries?
    es = Elasticsearch()
    for doc in filterFiles(inputDir, accept):

        parsed = parser.from_file(doc)
        parsed["metadata"].pop(u"resourceName", None)

        resp = es.index(index="example1", doc_type="polar", id="file:"+doc, body=parsed)

        if resp["created"]:
            continue
        else:
            print "Lost docID: ", doc
"""