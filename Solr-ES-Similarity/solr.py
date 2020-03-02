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
import requests, json, time

current_milli_time = lambda: int(round(time.time() * 1000))

class Solr(object):
    """
    Solr client for querying, posting and committing docs
    """

    def __init__(self, solr_url):

        self.update_url = solr_url.rstrip('/') + '/update/json'
        self.query_url = solr_url.rstrip('/') + '/select'
        self.headers = {"content-type": "application/json"}

    def post_items(self, items, commit=False, softCommit=False):
        """
        Post list of items to Solr
        """

        url = self.update_url
        # Check either to do soft commit or hard commit
        if commit == True:
            url = url + '?commit=true'
        elif softCommit or 'soft' == commit:
            url = url + '?softCommit=true'

        resp = requests.post(url, data=json.dumps(items).encode('utf-8', 'replace'), headers=self.headers)

        if not resp or resp.status_code != 200:
            print('Solr posting failed')
            return False
        return True


    def post_iterator(self, iter, commit=False, softCommit=False, buffer_size=100, progress_delay=2000):
        """
        Posts all the items yielded by the input iterator to Solr;
        The documents will be buffered and sent in batches
        :param iter: generator that yields documents
        :param commit: commit after each batch? default is false
        :param softCommit: soft commit after each call ? default is false
        :param buffer_size: number of docs to buffer and post at once
        :param progress_delay: the number of milliseconds of
        :return: (numDocs, True) on success, (numDocs, False) on failure
        """

        buffer = []
        count = 0
        num_docs = 0
        tt = current_milli_time()
        for doc in iter:
            num_docs += 1
            buffer.append(doc)

            if len(buffer) >= buffer_size:
                # buffer full, post them
                count += 1
                if self.post_items(buffer, commit=commit, softCommit=softCommit):
                    # going good, clear them all
                    del buffer[:]
                else:
                    print(('Solr posting failed. batch number=%d' % count))
                    return (num_docs, False)

            if (current_milli_time() - tt) > progress_delay:
                tt = current_milli_time()
                print(("%d batches, %d docs " % (count, num_docs)))

        res = True
        if len(buffer) > 0:
            res = self.post_items(buffer, commit=commit, softCommit=softCommit)
        return (num_docs, res)

    def commit(self):
        '''
        Commit index
        '''
        resp = requests.post(self.update_url + '?commit=true')
        if resp.status_code == 200:
            self.posted_items = 0
        return resp


    def query_iterator(self, query='*:*', start=0, rows=20, limit=None, **kwargs):
        """
        Queries solr server and returns Solr response as dictionary
        returns None on failure, iterator of results on success
        """
        payload = {
            'q': query,
            'rows': rows,
            'wt': 'python'
        }

        if kwargs:
            for key in kwargs:
                payload[key] = kwargs.get(key)

        total = start + 1
        count = 0
        while start < total:
            if limit and count >= limit: #terminate
                break

            payload['start'] = start
            print('start={0}   total={1}'.format(start, total))

            resp = requests.get(self.query_url, params=payload)
            if not resp:
                print("No response from Solr Server!")
                break

            if resp.status_code == 200:
                resp = eval(resp.text)
                total = resp['response']['numFound']
                for doc in resp['response']['docs']:
                    start += 1
                    count += 1
                    yield doc
            else:
                print(resp)
                print("Something went wrong when querying solr")
                print("Solr query params ", payload)
                break