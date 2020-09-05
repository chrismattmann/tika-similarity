import sys, csv, pickle
from pprint import pprint

def flickr_eval():
    return None

def raise_eval(eval_file):

    ground_truth = {'buildings': [],
                    'outdoor': [],
                    'people': [],
                    'nature': [],
                    'objects': [],
                    'Indoor': [],
                    'landscape': []
                    }

    with open(eval_file, 'rb') as inF:
        reader = csv.reader(inF)
        next(reader)
        for row in reader:
            labels = [label.strip() for label in row[-1].strip().split(';')]

            for label in labels:
                ground_truth[label].append(row[0].strip())

        pprint(ground_truth)

        pickle.dump(ground_truth, open("ACM_raise1k_ground_labels.p", "wb"))


if __name__ == '__main__':

    if sys.argv[1] == "raise":
        raise_eval(sys.argv[2])

    elif sys.argv[1] == "flickr":
        raise_eval(sys.argv[2])

    else:
        print("Argument 1, dataset 'raise' or 'flickr'")
        print("Argument 2, ground truth file")