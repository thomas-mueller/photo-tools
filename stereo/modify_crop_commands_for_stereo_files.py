#! /usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os, re, sys


if __name__ == "__main__":
	parser = OptionParser(usage="usage: %prog [options] <CROP SCRIPT 1> ...",
						  description="Edit crop script by adjusting the x-dimensions for the double width.")

	parser.add_option("-i", "--input-dir", default="$1", help="Input directory. [Default: $1]")
	parser.add_option("-o", "--output-dir", default="$2", help="Output directory. [Default: $2]")
	parser.add_option("-a", "--additional-params", default="-verbose -quality 90%", help="Additional parameters for convert. [Default: \"-verbose -quality 90%\"]")
	parser.add_option("--overwrite", action="store_true", default=False, help="Overwrite input scripts. [Default: False]")

	(options, args) = parser.parse_args()
	
	if len(args) < 1:
		print "ERROR: no inputs specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	for inputFileName in args:
		outputFileName = inputFileName
		if not options.overwrite:
			outputFileName = outputFileName.rpartition(".")
			outputFileName = outputFileName[0]+".2x"+outputFileName[1]+outputFileName[2]
		
		with open(inputFileName, "r+" if options.overwrite else "r") as inputFile:
			inputFileContent = inputFile.read()
			outputFileContent = ""
			for index, inputFileLine in enumerate(inputFileContent.splitlines()):
				outputFileLine = inputFileLine
				
				regexMatch = re.match(r"(?P<a>.*)convert (?P<in>.+) (?P<aa>.*)-crop (?P<w>\d+)x(?P<h>\d+)\+(?P<x>\d+)\+(?P<y>\d+)(?P<aaa>.*) (?P<out>.+)(?P<aaaa>.*)", inputFileLine)
				if regexMatch:
					regexMatchDict = regexMatch.groupdict()
					
					if regexMatchDict["x"] != "0": print "ERROR: Line "+str(index+1)+" \""+inputFileLine+"\" cannot be treated correctly!."
					
					outputFileLine = regexMatchDict["a"] + "convert "
					outputFileLine += os.path.join(options.input_dir, os.path.basename(os.path.abspath(regexMatchDict["in"])))
					outputFileLine += " " + regexMatchDict["aa"] + " " + options.additional_params + " -crop "
					outputFileLine += str(int(regexMatchDict["w"]) * 2)+"x"+regexMatchDict["h"]+"+"+regexMatchDict["x"]+"+"+regexMatchDict["y"]
					outputFileLine += regexMatchDict["aaa"] + " "
					outputFileLine += os.path.join(options.output_dir, os.path.basename(os.path.abspath(regexMatchDict["out"])))
					outputFileLine += regexMatchDict["aaaa"]
				
				outputFileContent += (outputFileLine + "\n")
			
			if options.overwrite: inputFile.write(outputFileContent)
			else:
				with open(outputFileName, "w") as outputFile: outputFile.write(outputFileContent)
				
			print "New crop commands stored: \"" + inputFileName + "\" --> \"" + outputFileName + "\"."

