import math

def stringify(attribute_value):
    if isinstance(attribute_value, list):
        return str((", ".join(attribute_value)).encode('utf-8').strip())
    else:
        return str(attribute_value.encode('utf-8').strip())


class Vector:
    '''
    An instance of this class represents a vector in n-dimensional space
    '''

    def __init__(self, features):
        '''
        Create a vector
        @param metadata features 
        '''
        na_metadata = ["resourceName"]
        for na in na_metadata:
            features.pop(na, None)

        self.features = {}
        for key in features:
            self.features[key] = len(stringify(features[key]))

    
    '''
    def __str__(self):        
        vector_str = "( {0} ): \n".format(self.)
        if self.features:
            for key in self.features:
                vector_str += " {1}: {2} \n".format(key, self.features[key])
        return vector_str+"\n"
    '''

    def getMagnitude(self):
        totalMagnitude = 0.0
        for key in self.features:
            totalMagnitude += self.features[key] ** 2
        return math.sqrt(totalMagnitude)


    def dotProduct(self, anotherVector):
        '''
        A = ax+by+cz
        B = mx+ny+oz
        A.B = a*m + b*n + c*o
        '''        
        dot_product = 0.0
        intersect_features = set(self.features) & set(anotherVector.features)
        
        for feature in intersect_features:
            dot_product += self.features[feature] * anotherVector.features[feature]
        return dot_product


    def cosTheta(self, v2):
        '''
        cosTheta = (V1.V2) / (|V1| |V2|)
        cos 0 = 1 implies identical documents
        '''
        return self.dotProduct(v2) / (self.getMagnitude() * v2.getMagnitude())