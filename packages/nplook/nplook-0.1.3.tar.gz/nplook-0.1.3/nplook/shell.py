
from __future__ import print_function
import sys
import nplook
import glob
from optparse import OptionParser

def main():
    examples = []
    examples.append(("data.npy", "summarizes the ndarray in data.npy"))
    examples.append(("data.npz", "summarizes the dictionary in data.npz"))
    examples.append(("*.npz", "summarizes all npz files in the directory"))
    examples.append(("", "summarizes all files in the directory"))

    ex_str = "\n".join(["  %prog {0:<18}{1}".format(tup[0], tup[1]) for tup in examples])

    usage = "Usage: %prog [options] <file> [<file> ...]\n\nExamples:\n{0}".format(ex_str)
    parser = OptionParser(usage=usage, version="%prog {0}".format(nplook.__version__))

    (options, args) = parser.parse_args()
    
    if args:
        filenames = args
    else:
        filenames = glob.glob("*")

    i = 0
    for filename in filenames:
        summary = nplook.summarize(filename)
        if summary: 
            if i != 0: print()
            print(summary)
            i += 1

    if i == 0:
        print("No files that can be summarized matched your query")
