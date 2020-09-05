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


import itertools
import features as feat
import math
import re

#split a string when we see a transition from one type to another say alpha, numeric, spl chars.
def break_natural_boundaries(string):
    stringbreak=[]
    if len(string.split(' ')) > 1:
        stringbreak = string.split(' ')
    else:
        spl = '[a-z][\%|\$|\^|\*|\@|\!|\_|\-|\(|\)|\:|\;|\'|\"|\{|\}|\[|\]|]'
        up = '[A-Z]'
        low = '[a-z]'
        num = '\d'



        matchindex = set()
        matchindex.update(set(m.start() for m in re.finditer(up + low, string)))
        matchindex.update(set(m.start() for m in re.finditer(low + up, string)))
        matchindex.update(set(m.start() for m in re.finditer(num + up, string)))
        matchindex.update(set(m.start() for m in re.finditer(up + num, string)))
        matchindex.update(set(m.start() for m in re.finditer(low + num, string)))
        matchindex.update(set(m.start() for m in re.finditer(num + low, string)))
        matchindex.update(set(m.start() for m in re.finditer(spl + up, string)))
        matchindex.update(set(m.start() for m in re.finditer(up + spl, string)))
        matchindex.update(set(m.start() for m in re.finditer(low + spl, string)))
        matchindex.update(set(m.start() for m in re.finditer(spl + low, string)))
        matchindex.update(set(m.start() for m in re.finditer(spl + num, string)))
        matchindex.update(set(m.start() for m in re.finditer(num + spl, string)))
        matchindex.add(len(string)-1)
        matchindex = sorted(matchindex)
        start = 0

        for i in matchindex:
            end = i
            stringbreak.append(string[start:end + 1])
            start = i+1
    return stringbreak


def meta_levenshtein(string1,string2,Sim='levenshtein',theta=0.5,strict=-1,idf=dict()):

    ''' Implements ideas from the paper : Robust Similarity Measures for Named Entities Matching by Erwan et al.
    Sim = jaro_winkler, levenshtein : can be chosen as the secondary matching function.
    theta is the secondary similarity threshold: If set higher it will be more difficult for the strings to match.
    strict=-1 for doing all permutations of the substrings
    strict=1 for no permutations
    idf=provide a dictionary for {string(word),float(idf od the word)}: More useful when mathings multi word entities (And word importances are very important)
    like: 'harry potter', 'the wizard harry potter'
    '''

    # set the secondary simlarity function
    if Sim == 'levenshtein':
        simf = lambda x, y: feat.levenshtein_similarity(str(x, 'utf-8'), str(y, 'utf-8'))
    elif Sim=='jaro_winkler':
        simf = lambda x, y: feat.jaro_winkler_similarity(str(x, 'utf-8'), str(y, 'utf-8'))

    # set the idf and normalization functions
    if len(idf)>0:
        idf=lambda x,y :idf[x]*idf[y]
        norm=lambda x,y,ex,ey: math.sqrt(sum([i**2 for i in ex]))*math.sqrt(sum([i**2 for i in ey]))
    else:
        idf=lambda x,y:1
        norm=lambda x,y,ex,ey:max(len(x),len(y))

    # break the string down into sub-strings ( if it has not spaces already)

    string1break=break_natural_boundaries(string1)
    string2break=break_natural_boundaries(string2)

    # swap the bigger one to string2
    if len(string1break)>len(string2break):
        temp=string1break
        string1break=string2break
        string2break=temp

    # make permutations of srtingbreak

    perm1 = []
    perm2 = []

    if strict==-1:
        perm1=itertools.permutations(string1break)
        perm2=itertools.permutations(string2break)
    elif strict==1:
        perm1.append(string1break)
        perm2.append(string2break)



    # Do secondary matching for each permutation and each (Levenshtein) shift (E=edges that qualify/remain after applying the threshold: theta)
    bestscore=0.0
    for st1 in perm1:
        for st2 in perm2:
            for k in range (0,len(st2)-len(st1)+1):
                permscore = 0.0
                E1=[]
                E2=[]
                for i in range(0,len(st1)):
                    # calculate the secondary similarites for a fixed instance
                    simtemp=simf(st1[i],st2[i+k])*idf(st1[i],st2[i+k])
                    if simtemp>=theta:
                        E1.append(st1[i])
                        E2.append(st2[i+k])
                        permscore+=simtemp
                if permscore>bestscore:
                    bestscore=permscore




    bestscore=bestscore/norm(st1,st2,E1,E2)
    return bestscore







if __name__ == '__main__':
    #usage example
    print(meta_levenshtein('abacus1cat','cat1cus'))

