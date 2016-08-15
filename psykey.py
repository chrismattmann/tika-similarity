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
import argparse
import csv
import features as feat


# A class to do stylstic extractions from text: To use programatically, initialize the class. This will calculate different kinds of stylistic features from the text,
# eg. as many times it finds a punctuation it will add the word 'punc' to the 'featspace list'. Similarly, all the extractions are added to 'featspace'
# in form of signatures. To access a specific feature, call that specific method from the object of the class.
class psykey:
    def __init__(self, text, wordlistfolder):
        self.text = text
        self.tokens = nltk.word_tokenize(text)
        self.sentenses = nltk.sent_tokenize(text)
        self.tags = nltk.pos_tag(self.tokens)

        self.featspace = []

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

    # Counts a specific POS tags
    def countPOS(self, featspace, postag):
        tags = self.tags
        count = 0
        for word in tags:
            if word[1] == postag:
                count += 1
                featspace.append(postag)

    # Counts number of words
    def words(self, featspace):
        tokens = self.tokens
        featspace.extend(tokens)
        return len(tokens)

    # Count number of sentenses
    def sentence_count(self, featspace):
        sentences = self.sentenses
        count = len(sentences)
        for i in range(0, count):
            featspace.append('sentcount')
        return count

    # Counds the average number of words per sentence
    def words_per_sentence(self, featspace):
        token_length = len(self.tokens)
        sentences_length = len(self.sentenses)
        count = int(token_length / sentences_length)
        for i in range(0, count):
            featspace.append('wordspersentence')

    # Counts the number of big words: words bigger than 6 chars
    def big_word_count(self, featspace):
        count = 0
        tokens = self.tokens
        for word in tokens:
            if len(word) > 6:
                count += 1
                featspace.append('bigword')

    # Counts the total number of punctuations in the text
    def punc_count(self, featspace):
        count = 0
        tokens = self.tokens
        punctuations = string.punctuation.replace('.', '')
        for word in tokens:
            if word in punctuations:
                count += 1
                featspace.append('punc')

    # Counts teh number of numerical words in text
    def number_count(self, featspace):
        count = 0
        tokens = self.tokens
        for word in tokens:
            flag = 0
            for ch in word:
                if ch in '0123456789':
                    flag = 1
                    break
            if flag == 1:
                featspace.append('numbers')
                count += 1

    # Creates bigrams
    def bigrams(self, featspace):
        tokens = self.tokens
        for count in range(0, len(tokens) - 1):
            featspace.append(tokens[count] + tokens[count + 1])

    # Opens the folder with all the wordlists. matches the words in text with the words in each file. If match found, creates a feature/signature with the name of the
    # file.
    def psykfeatspace(self, featspace, wordlistfolder):
        tokens = self.tokens
        for filename in os.listdir(wordlistfolder):
            if '.txt' in filename:
                names = [line.strip() for line in open(os.path.join(wordlistfolder , filename), 'r')]
            else:
                continue
            for token in tokens:
                if token in names:
                    featspace.append(filename.replace('.txt', ''))

    # Creates stemmed words from the text
    def stem(self, featspace):
        tokens = self.tokens
        for token in tokens:
            featspace.append(stem(token))


def ClaculatePairwise(inputdir, outputcsv, wordlists):
    files = os.listdir(inputdir)
    calculated=set()
    with open(outputcsv, "wb") as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["file1", "file2", "Similarity_score"])
        for file1 in files:
            for file2 in files:
                if '.txt' in file1 and '.txt' in file2 and file1+'\t'+file2 not in calculated and file1!=file2:
                    calculated.add(file1+'\t'+file2)
                    calculated.add(file2 + '\t' + file1)
                    text1 = open(os.path.join(inputdir,file1), 'rU')
                    text2 = open(os.path.join(inputdir,file2), 'rU')
                else:
                    continue
                raw1 = text1.read()
                raw2 = text2.read()
                psykey1 = psykey(raw1, wordlists)
                psykey2 = psykey(raw2, wordlists)

                score = feat.get_cosine_similarity(psykey1.featspace, psykey2.featspace)
                a.writerow([file1, file2, score])

                text1.close()
                text2.close()


if __name__ == '__main__':
    argParser = argparse.ArgumentParser('Cosine Similarity based on stylistic features')
    argParser.add_argument('--inputDir', required=True,help='path to directory for storing the output CSV File, containing pair-wise Cosine similarity on stylistic features')
    argParser.add_argument('--outCSV', required=True, help='path to output file')
    argParser.add_argument('--wordlists', required=True, help='wordlist folder with files containing lists of words (one per line)')
    args = argParser.parse_args()

    if args.inputDir and args.outCSV and args.wordlists:
        ClaculatePairwise(args.inputDir, args.outCSV, args.wordlists)

