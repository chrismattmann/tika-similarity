# author: Asitang Mishra
# asitang.mishra@jpl.nasa.gov
# asitang@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import nltk
import string
import os
from stemming.porter2 import stem
import io
import sys

#A class to do styllic extractions from text. Initializing the class creates/fills up all the lists
class psykey:

    def __init__(self,text,wordlistfolder):
        self.text=text
        self.tokens=nltk.word_tokenize(text)
        self.sentenses=nltk.sent_tokenize(text)
        self.tags = nltk.pos_tag(self.tokens)

        self.featspace=[]

        self.psykfeatspace(self.featspace, wordlistfolder)
        self.bigrams(self.featspace)
        self.number_count(self.featspace)
        self.punc_count(self.featspace)
        self.big_word_count(self.featspace)
        self.words_per_sentence(self.featspace)
        self.sentence_count(self.featspace)
        self.countPOS(self.featspace, 'CC')
        self.countPOS(self.featspace, 'NP')
        self.countPOS(self.featspace, 'NNP')
        self.words(self.featspace)
        self.stem(self.featspace)


    def countPOS(self,featspace,postag):
        tags=self.tags
        count=0
        for word in tags:
            if word[1] == postag:
                count+=1
                featspace.append(postag)

    def words(self,featspace):
        tokens=self.tokens
        featspace.extend(tokens)
        return len(tokens)

    def sentence_count(self,featspace):
        sentences=self.sentenses
        count=len(sentences)
        for i in range(0,count):
            featspace.append('sentcount')
        return count

    def words_per_sentence(self,featspace):
        token_length=len(self.tokens)
        sentences_length=len(self.sentenses)
        count=int(token_length/sentences_length)
        for i in range(0,count):
            featspace.append('wordspersentence')

    def big_word_count(self,featspace):
        count=0
        tokens=self.tokens
        for word in tokens:
            if len(word)>6:
                count+=1
                featspace.append('bigword')

    def punc_count(self,featspace):
        count=0
        tokens=self.tokens
        punctuations=string.punctuation.replace('.','')
        for word in tokens:
            if word in punctuations:
                count+=1
                featspace.append('punc')


    def number_count(self,featspace):
        count=0
        tokens=self.tokens
        for word in tokens:
            flag=0
            for ch in word:
                if ch in '0123456789':
                    flag=1
                    break
            if flag==1:
                featspace.append('numbers')
                count+=1

    def bigrams(self,featspace):
        tokens = self.tokens
        for count in range(0,len(tokens)-1):
            featspace.append(tokens[count]+tokens[count+1])

    def psykfeatspace(self,featspace,wordlistfolder):
        tokens=self.tokens
        for filename in os.listdir(wordlistfolder):
            names = [line.strip() for line in open(wordlistfolder + '/' + filename, 'r')]
            for token in tokens:
                if token in names:
                    featspace.append(filename.replace('.txt', ''))

    def stem(self,featspace):
        tokens=self.tokens
        for token in tokens:
            featspace.append(stem(token))












