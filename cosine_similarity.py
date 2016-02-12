from tika import parser
from vector import Vector
import os, itertools, argparse, csv

def filterFiles(inputDir, acceptTypes):
    filename_list = []

    for root, dirnames, files in os.walk(inputDir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in files:
            if not filename.startswith('.'):
                filename_list.append(os.path.join(root, filename))

    filename_list = [filename for filename in filename_list if parser.from_file(filename)]
    if acceptTypes:
        filename_list = [filename for filename in filename_list if str(parser.from_file(filename)['metadata']['Content-Type'].encode('utf-8')).split('/')[-1] in acceptTypes]
    else:
        print "Accepting all MIME Types....."

    return filename_list


def computeScores(inputDir, outCSV, acceptTypes):
    
    with open(outCSV, "wb") as outF:
        a = csv.writer(outF, delimiter=',')
        a.writerow(["x-coordinate","y-coordinate","Similarity_score"])        

        files_tuple = itertools.combinations(filterFiles(inputDir, acceptTypes), 2)
        for file1, file2 in files_tuple:

            row_cosine_distance = [file1, file2]
            
            file1_parsedData = parser.from_file(file1)
            file2_parsedData = parser.from_file(file2)

            v1 = Vector(file1_parsedData["metadata"])
            v2 = Vector(file2_parsedData["metadata"])

            row_cosine_distance.append(v1.cosTheta(v2))            

            a.writerow(row_cosine_distance)  
    


if __name__ == "__main__":

    argParser = argparse.ArgumentParser('Cosine similarity based on Metadata values')
    argParser.add_argument('--inputDir', required=True, help='path to directory containing files')
    argParser.add_argument('--outCSV', required=True, help='path to directory for storing the output CSV File, containing pair-wise Cosine similarity Scores')
    argParser.add_argument('--accept', nargs='+', type=str, help='Optional: compute similarity only on specified IANA MIME Type(s)')
    args = argParser.parse_args()

    if args.inputDir and args.outCSV:
        computeScores(args.inputDir, args.outCSV, args.accept)