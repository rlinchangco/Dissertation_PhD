#!/usr/bin/python -tt

import collections
import getopt
import sys
import os
from nltk.stem.porter import *


def tsvParser(tsv_File):
    """
    This searches primarily for predicates.
    Will be abstracted for:
    # docs,
    # unique entities,
    # total unique predicates,
    # total predicates (relns)
    """
    stemmer = PorterStemmer()
    rel_Set = set()
    rel_Dict = collections.defaultdict(list)

    with open(tsv_File) as input:
        for line in input:
            line_Array = line.replace("\"", "").split("\t")
            subjectID = line_Array[0]
            subjectTerm = (line_Array[1], line_Array[2])
            objectID = line_Array[4]
            objectTerm = (line_Array[5], line_Array[6])
            hitText = line_Array[7]
            doc = line_Array[10]

            # split by whitespace, identify longest word, stem
            predicatePhrase = line_Array[3]
            predicatePhrase = predicatePhrase.decode('utf-8')
            predicateList = predicatePhrase.split()
            # sorted in ascending order
            sortedList = sorted(predicateList, key=len)
            if len(sortedList) < 1:
                print line
            # following line changes for stemming vs. no stemming
            predicate = stemmer.stem(sortedList[-1])
            #predicate = sortedList[-1]

            # REMOVE PREDICATE PHRASE
            if predicate not in rel_Set:
                rel_Dict[predicate] = [[subjectID, objectID,
                                        subjectTerm, objectTerm, hitText, doc]]
                rel_Set.add(predicate)
            else:
                rel_Dict[predicate].append(
                    [subjectID, objectID, subjectTerm, objectTerm, hitText, doc])
    # print pred_Set
    return rel_Dict


def multiFileParser(filePath):
    rel_Dict = collections.defaultdict(list)
    # PARSE THROUGH MULTIPLE DIRECTORIES
    fileList = []
    unique_docs = set()

    for root, dirs, files in os.walk(filePath):
        for name in files:
            if name.endswith(".tsv"):
                fileList.append(os.path.join(root, name))

    for oneFile in fileList:
        parsed_File = tsvParser(oneFile)
        for predicate in parsed_File:
            if predicate in rel_Dict:
                for hit in parsed_File[predicate]:
                    rel_Dict[predicate].append(hit)
            else:
                rel_Dict[predicate] = parsed_File[predicate]

    print "Number of files:\t%d" % len(fileList)
    return rel_Dict


def main(argv):
    """
    command line arguments bit from
    http://www.tutorialspoint.com/python/python_command_line_arguments.htm
    """
    tsv_In = ""
    tsv_Out = ""

    try:
        opts, args = getopt.getopt(
            argv, "hi:o:", ["help", "tsvInput=", "tsvOutput="])
    except getopt.GetoptError:
        print 'WRONG'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Try Again'
            sys.exit()
        elif opt in ("-i", "--tsvInput"):
            tsv_In = arg
        elif opt in ("-o", "--tsvOutput"):
            tsv_Out = arg

    if not tsv_In:
        print "Please provide input"
        sys.exit(2)

    totalRels = 0
    highestScore = 0
    highestPredicate = ""
    aveScore = 0
    totalList = []
    # Dictionary structure: { predicate : [[subjectID, objectID, subjectTerm,
    # objectTerm, hitText]]}
    full_List = multiFileParser(tsv_In)
    doc_set = set()

    for predicate in full_List:
        totalList.append((len(full_List[predicate]), predicate))
        totalRels = len(full_List[predicate]) + totalRels
        for lineList in full_List[predicate]:
            doc_set.add(lineList[5])

        if len(full_List[predicate]) > highestScore:  # and len(full_List[predicate]) != 7386 and len(full_List[predicate]) != 3317 and len(full_List[predicate]) != 3114 and len(full_List[predicate]) != 2384 and len(full_List[predicate]) != 2220 and len(full_List[predicate]) != 2129 and len(full_List[predicate]) != 2005 and len(full_List[predicate]) != 1856 and len(full_List[predicate]) != 1832 and len(full_List[predicate]) != 1568 and len(full_List[predicate]) != 1544 and len(full_List[predicate]) != 1453 and len(full_List[predicate]) != 1396 and len(full_List[predicate]) != 1292 and len(full_List[predicate]) != 1221 and len(full_List[predicate]) != 1020:
            highestScore = len(full_List[predicate])
            highestPredicate = predicate
            aveScore += len(full_List[predicate])

    # Allow for filtered single word predicates

    totalList.sort(reverse=True)
    # print "Highest predicate count:\t%d\t%s" % (highestScore, highestPredicate)
    # print "Average predicate count:\t%f" % float(aveScore/len(full_List))
    tsv_Out = open(tsv_Out, "w")
    tsv_Out.write("Count\tPredicate\n")
    for i in totalList:
        outLine = "%d\t%s\n" % (i[0], i[1])
        tsv_Out.write(outLine.encode('utf-8'))
        # if i[0] <= 10 and i[0] >= 5:
        #    print i
    print "Unique predicates:\t%d" % len(full_List)
    print "Total Relationships:\t%d" % totalRels
    print "Total Documents:\t%d" % len(doc_set)

if __name__ == '__main__':
    main(sys.argv[1:])
