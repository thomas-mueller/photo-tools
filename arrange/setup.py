#! /usr/bin/env python

from optparse import OptionParser
import datetime, os, re, sys

import tools



# =================================================================================================	
def setupDirs(options, doPanos=False, log=False):
	projectSubDir = str(options.year)+"_"+str(options.project_number)+"_"+options.project_name if options.year and options.project_number and options.project_name else ""
	for use in tools.getUses(options):
		dirToCreate = os.path.join(tools.getDir(options.base_dir, use), str(options.year), projectSubDir)
		tools.makeDir(dirToCreate, log=log)
		
		if doPanos and use=="pano":
			for panoName in options.panos: tools.makeDir(os.path.join(dirToCreate, panoName), log=log)



# =================================================================================================	
def determineNumber(options):
	if not options.project_number:
		dirs = []
		for use in tools.getUses(options):
			subDir = os.path.join(tools.getDir(options.base_dir, use), str(options.year))
			if not os.path.exists(subDir):
				os.makedirs(subDir)
			
			dirsTemp = map(lambda dirEntry: os.path.join(subDir, dirEntry), os.listdir(subDir))
			dirs.extend(filter(lambda dirEntry: os.path.isdir(dirEntry), dirsTemp))
		
		projectNumbers = map(lambda dirName: int(re.match(r".*/\d*_(?P<number>\d*)_\w*", dirName).groupdict()["number"]), dirs)
		options.project_number = (max(projectNumbers) if len(projectNumbers) > 0 else 0) + 1
	
	options.project_number = tools.getNumberFilledString(options.project_number, tools.NUMBER_OF_DIGITS)
	
	return options.project_number



###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options] PROJECT_NAME",
			              description="Setup of directory structure for a new project. The name of the new project can either be passed as a parameter or a simple argument.")

	parser.add_option("--base-dir", default=".", help="Base directory containing at least directory 2D [Default: .].")
	parser.add_option("--year", type="int", help="Year for project [Default: this year].")
	parser.add_option("--project-number", type="int", help="Number for project [Default: auto-determined].")
	parser.add_option("--project-name", help="New project name")
	
	parser.add_option("--no-jpeg", action="store_true", default=False, help="Do not create a project subdirectory in for JPEG [Default: False].")
	parser.add_option("--no-mov", action="store_true", default=False, help="Do not create a project subdirectory in for MOV [Default: False].")
	parser.add_option("--no-pano", action="store_true", default=False, help="Do not create a project subdirectory in for PANO [Default: False].")
	parser.add_option("--no-raw", action="store_true", default=False, help="Do not create a project subdirectory in for RAW [Default: False].")
	parser.add_option("--no-3d", action="store_true", default=False, help="Do not create a project subdirectory in for 3D [Default: False].")
	
	parser.add_option("--n-panos", type="int", default=0, help="Number of panorama directories to create [Default: 0]. If panorama project names are specified, this option is ignored.")
	parser.add_option("--panos", help="List (ws separated) of panorama project names.")

	(options, args) = parser.parse_args()
	
	# check project name
	if not options.project_name and len(args) > 0:
		projectNameArgs = reduce(lambda arg1, arg2: arg1+"_"+arg2, args)
		options.project_name = projectNameArgs
	
	if not options.project_name:
		print "ERROR: no project name specied!"
		print ""
		parser.print_help()
		sys.exit(1)

	# check base directory
	if not os.path.exists(tools.getDir(options.base_dir, "2d")):
		print "ERROR: base directory %s does not contain the 2D subdirectory!" % options.base_dir
		print ""
		parser.print_help()
		sys.exit(1)
	
	# determine year and number and create the directories
	if not options.year: options.year = str(datetime.date.today().year)
	
	determineNumber(options)
	
	# panorama subdirectories
	if not options.no_pano:
		if options.panos: options.panos = options.panos.split()
		else: options.panos = []
		
		if options.n_panos > len(options.panos): options.panos.extend((options.n_panos-len(options.panos)) * [options.project_name])
		
		if len(options.panos) > 0:
			numberOfDigits = max(tools.NUMBER_OF_DIGITS, tools.getNumberOfDigits(len(options.panos)))
			for index, panoName in enumerate(options.panos): options.panos[index] = tools.getNumberFilledString(index+1, numberOfDigits)+"_"+panoName
	
	# set up directories
	setupDirs(options, doPanos=True, log=True)
		


if __name__ == "__main__": main()

