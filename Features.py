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





if __name__ == '__main__':
    data1=[1,2,3,3,2,1]
    data2=[4,5,6,6,5,4]

    area,error=gaussian_overlap(data1,data2)

    print area

