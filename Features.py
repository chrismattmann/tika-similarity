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


from collections import Counter
import jellyfish
import scipy.stats
from scipy import integrate
import numpy as np
import datetime
import math

#Each function takes two inputs and give back a feature score (a distance measure)



def levenshtein_similarity(s, t):
    """ Levenshtein Similarity """

    Ns = len(s);
    Nt = len(t);

    lev_sim = 1.0 - (jellyfish.levenshtein_distance(s, t)) / float(max(Ns, Nt))

    return lev_sim


def jaro_winkler_similarity(s, t):
    """ Jaro-Winkler Similarity """

    jw_sim = jellyfish.jaro_winkler(s, t)


    return jw_sim


#Get an aggregate of terms in your text
def text_to_vector(text):
    return Counter(text)


#get cosine similarity between two document vectors
def get_cosine(vec1, vec2):
    import math

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


#get cosine similarity between texts
def CosineSim(text1,text2):
    vec1=text_to_vector(text1)
    vec2=text_to_vector(text2)
    dist=get_cosine(vec1,vec2)
    return dist




#finds the area overlap between two guassian/normal distributions. First find the mean and std of a data sample
def gaussian_overlap(data1,data2):


    mean1=np.mean(data1)
    mean2=np.mean(data2)

    std1=np.std(data1)
    std2=np.std(data1)

    f = lambda x: min(scipy.stats.norm(mean1, std1).pdf(x),scipy.stats.norm(mean2, std2).pdf(x))
    area, error=integrate.quad(f, -np.inf,+np.inf)

    area = float(area)
    if math.isnan(area):
        area=0.0
    return area


#Breaks down the epoch time stamp into day and the specific minute of the day
def breakdown_epoch(epoch):
    hour=datetime.datetime.fromtimestamp(epoch).strftime('%H')
    minute=datetime.datetime.fromtimestamp(epoch).strftime('%M')
    day=datetime.datetime.fromtimestamp(epoch).strftime('%A')

    daymap={'Sunday':1,'Monday':2,'Tuesday':3,'Wednesday':4,'Thursday':5,'Friday':6,'Saturday':7}
    minute=int(minute)
    hour=int(hour)
    day=daymap[day]
    totalminutes=(hour*60)+minute

    return day,totalminutes


if __name__ == '__main__':
    data1=[1,2,3,3,2,1]
    data2=[4,5,6,6,5,4]

    area,error=gaussian_overlap(data1,data2)

    print area

