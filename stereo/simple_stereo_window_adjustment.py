#! /usr/bin/env python

from optparse import OptionParser
import copy, glob, os, subprocess, sys, time



###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options] <DIRECTORY1 | FILE1> ...",
			              description="Shift stereo window of L-R 2D photos by a fixed number of pixels.")

	parser.add_option("--move-by", default="125", type=int, help="Number of pixels to shift the two photos. Must be positive. [Default: 125]")
	parser.add_option("--output-dir", help="Specify output directory for the corrected files in order not to overwrite the existing ones.")

	(options, args) = parser.parse_args()
	
	if len(args) < 1:
		print "ERROR: no inputs specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if not options.output_dir:
		overwrite = raw_input("Do you really want to overwrite the inputs? [y|N] ").lower().startswith("y")
		if not overwrite: sys.exit(0)

	inputFiles = sum(map(lambda arg: glob.glob(os.path.join(arg, "*")) if os.path.isdir(arg) else [arg], args), [])
	inputFilesString = reduce(lambda a, b: str(a) + " " + str(b), inputFiles)
	
	command = "mogrify -verbose" + ((" -path "+options.output_dir) if options.output_dir else "") + " -shave "+str(options.move_by)+"x0 " + "<DIRECTORY1 | FILE1> ..."
	print command
	command = command.replace("<DIRECTORY1 | FILE1> ...", inputFilesString)
	os.system(command)

if __name__ == "__main__": main()

