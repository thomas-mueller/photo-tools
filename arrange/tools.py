#! /usr/bin/env python

import glob, math, os



# =================================================================================================
NUMBER_OF_DIGITS = 2
def getNumberOfDigits(numberOfItems): return math.floor(math.log10(numberOfItems)) + 1
def getNumberFilledString(number, numberOfDigits): return ("%s0%dd" % ("%", numberOfDigits)) % number



# =================================================================================================
def getDir(baseDir=".", use=None):
	subDir = ""
	if use:
		if use == "2d": subDir = "2D"
		elif use == "tmp": subDir = "2D/TMP"
		elif use == "jpeg": subDir = "2D/JPEG"
		elif use == "mov": subDir = "2D/MOV"
		elif use == "pano": subDir = "2D/PANO"
		elif use == "raw": subDir = "2D/RAW"
		elif use == "3d": subDir = "3D"
		elif use == "3d-3d": subDir = "3D/3D"
		elif use == "3d-l": subDir = "3D/L"
		elif use == "3d-r": subDir = "3D/R"
		elif use == "3d-spm": subDir = "3D/SPM"
	
	return os.path.join(baseDir, subDir)




# =================================================================================================	
def getUses(options):
	uses = []
	if not options.no_jpeg: uses.append("jpeg")
	if not options.no_mov: uses.append("mov")
	if not options.no_pano: uses.append("pano")
	if not options.no_raw: uses.append("raw")
	if not options.no_jpeg or not options.no_mov or not options.no_pano or not options.no_raw:
		uses.append("tmp")
	if not options.no_3d:
		uses.append("3d-3d")
		uses.append("3d-l")
		uses.append("3d-r")
		uses.append("3d-spm")
	
	return uses



# =================================================================================================	
def makeDir(directory, log=False):
	if not os.path.exists(directory):
		os.makedirs(directory)
		if log: print directory, "created."



# =================================================================================================
def multiglob(*patterns):
	globResult = []
	for pattern in patterns: globResult.extend(glob.glob(pattern))
	return sorted(list(set(globResult)))



# =================================================================================================
def determineYear(options):
	if not options.project_number:
		dirs = []
		for use in tools.getUses(options):
			subDir = os.path.join(tools.getDir(options.base_dir, use), options.year)
			dirsTemp = map(lambda dirEntry: os.path.join(subDir, dirEntry), os.listdir(subDir))
			dirs.extend(filter(lambda dirEntry: os.path.isdir(dirEntry), dirsTemp))
		
		projectNumbers = map(lambda dirName: int(re.match(r".*/\d*_(?P<number>\d*)_\w*", dirName).groupdict()["number"]), dirs)
		options.project_number = (max(projectNumbers) if len(projectNumbers) > 0 else 0) + 1




# =================================================================================================
def determineNumber(options):
	if not options.project_number:
		dirs = []
		for use in tools.getUses(options):
			subDir = os.path.join(tools.getDir(options.base_dir, use), options.year)
			dirsTemp = map(lambda dirEntry: os.path.join(subDir, dirEntry), os.listdir(subDir))
			dirs.extend(filter(lambda dirEntry: os.path.isdir(dirEntry), dirsTemp))
		
		projectNumbers = map(lambda dirName: int(re.match(r".*/\d*_(?P<number>\d*)_\w*", dirName).groupdict()["number"]), dirs)
		options.project_number = (max(projectNumbers) if len(projectNumbers) > 0 else 0) + 1

	options.project_number = tools.getNumberFilledString(options.project_number, tools.NUMBER_OF_DIGITS)
	
	return options.project_number

