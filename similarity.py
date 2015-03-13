import tika
from tika import parser
import os
import sys
import getopt
import json
tika.initVM()
import operator


_verbose = False
_helpMessage = '''

Usage: similarity [-v] [-f directory] [-c file1 file2]


Options:

-v, --verbose
	Work verbosely rather than silently.

-f, --directory [path to directory]
	read .jpg file from this directory

-c, --file [file1 file2]
	compare similarity of this two files

-h --help
	show help on the screen	
'''

def verboseLog(message):
	if _verbose:
		print >>sys.stderr, message

class _Usage(Exception):
	''' an error for arguments '''

	def __init__(self, msg):
		self.msg = msg

def main(argv = None):
	if argv is None:
		argv = sys.argv

	try:
		try:
			opts, args = getopt.getopt(argv[1:], 'hvf:c:', ['help', 'verbose', 'directory=', 'file=' ])
		except getopt.error, msg:
			raise _Usage(msg)

		if len(opts) ==0:
			raise _Usage(_helpMessage)

		dirFile = ""
		first_compare_file = ""
		second_compare_file = ""
		for option, value in opts:
			if option in ('-h', '--help'):
				raise _Usage(_helpMessage)

			elif option in ('-c', '--file'):
				
				#extract file names from command line
				if '-c' in argv :
					index_of_file_option = argv.index('-c')
				else :
					index_of_file_option = argv.index('--file')
				compare_file_name = argv[index_of_file_option+1 : ]
				first_compare_file = compare_file_name[0]
				second_compare_file = compare_file_name[1]

			elif option in ('-f', '--directory'):
				dirFile = value
			elif option in ('-v', '--verbose'):
				global _verbose
				_verbose = True

		union_feature_names = set()
		file_parsed_data = {}
		resemblance_scores = {}


		#count similarity for two given files
		if first_compare_file and second_compare_file:
			first_compare_file_path = os.path.join(dirFile, first_compare_file)
			second_compare_file_path = os.path.join(dirFile, second_compare_file)
			two_file_names = first_compare_file_path, second_compare_file_path


			# if file is not in directory or not a .jpg
			if not os.path.isfile(first_compare_file_path) :
				raise _Usage(_helpMessage)
			elif not os.path.isfile(second_compare_file_path) :
				raise _Usage(_helpMessage)
			else:

				for filename in two_file_names:


					# first compute the union of all features
					parsedData = parser.from_file(filename)
					file_parsed_data[filename] = parsedData["metadata"]
					union_feature_names = union_feature_names | set(parsedData["metadata"].keys())

				total_num_features = len(union_feature_names)

		#count all files similarity in directory
		else:

			for filename in os.listdir(dirFile):
				filename = os.path.join(dirFile, filename)
				if not os.path.isfile(filename) or not ".jpg"  in filename:
					continue

				# first compute the union of all features
				parsedData = parser.from_file(filename)
				file_parsed_data[filename] = parsedData["metadata"]
				union_feature_names = union_feature_names | set(parsedData["metadata"].keys())

			total_num_features = len(union_feature_names)



		# now compute the specific resemblance and containment scores
		for filename in file_parsed_data.keys():
			overlap = {}
			overlap = set(file_parsed_data[filename].keys()) & set(union_feature_names) 
			resemblance_scores[filename] = float(len(overlap))/total_num_features


		sorted_resemblance_scores = sorted(resemblance_scores.items(), key=operator.itemgetter(1), reverse=True)
		
		'''print "Resemblance:\n"
		for tuple in sorted_resemblance_scores:
			print os.path.basename(tuple[0].rstrip(os.sep))+","+str(tuple[1]) + "," + convertUnicode(file_parsed_data[tuple[0]])+'\n'''
		with open("similarity-scores.txt", "w") as f:
			f.write("Resemblance : \n")
			for tuple in sorted_resemblance_scores:
				f.write(os.path.basename(tuple[0].rstrip(os.sep))+","+str(tuple[1]) + "," + convertUnicode(file_parsed_data[tuple[0]])+'\n')

	except _Usage, err:
		print >>sys.stderr, sys.argv[0].split('/')[-1] + ': ' + str(err.msg)
		return 2


def convertUnicode( fileDict ) :
	fileUTFDict = {}
	for key in fileDict.keys():
		if isinstance(key, unicode) :
			key = key.encode('utf-8').strip()
		value = fileDict.get(key)
		if isinstance(value, unicode) :
			value = value.encode('utf-8').strip()
		fileUTFDict[key] = value
		
	return str(fileUTFDict)

if __name__ == "__main__":
	sys.exit(main())





	 