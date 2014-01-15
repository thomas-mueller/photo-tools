#! /usr/bin/env python

from optparse import OptionParser
import copy, glob, os, subprocess, sys, time



###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options] FILES",
			              description="Setup of directory structure for a new project. The name of the new project can either be passed as a parameter or a simple argument.")

	parser.add_option("--check", action="store_true", default=False, help="Check if file numbers and dates are in the same order. [Default: False]")
	parser.add_option("--ref-file", help="Reference file for determining the time shift.")
	parser.add_option("--ref-year", help="Correct year for reference file. [Default: year of reference file]")
	parser.add_option("--ref-month", help="Correct month for reference file. [Default: month of reference file]")
	parser.add_option("--ref-day", help="Correct day for reference file. [Default: day of reference file]")
	parser.add_option("--ref-hour", help="Correct hour for reference file. [Default: hour of reference file]")
	parser.add_option("--ref-minute", help="Correct minute for reference file. [Default: minute of reference file]")
	parser.add_option("--ref-second", help="Correct second for reference file. [Default: second of reference file]")

	(options, args) = parser.parse_args()
	
	if len(args) == 0:
		print "ERROR: no files to edit specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if not options.ref_file and not options.check:
		print "ERROR: either --check or --ref-file have to be specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	refExifTag = "DateTimeOriginal"
	
	inputFiles = sum(map(lambda arg: glob.glob(arg), args), [])
	inputFiles.sort()
	
	if options.ref_file:
		origYear = subprocess.check_output(["exiftool", "-d", "%Y", "-"+refExifTag, "-s3", options.ref_file]).replace("\n", "")
		origMonth = subprocess.check_output(["exiftool", "-d", "%m", "-"+refExifTag, "-s3", options.ref_file]).replace("\n", "")
		origDay = subprocess.check_output(["exiftool", "-d", "%d", "-"+refExifTag, "-s3", options.ref_file]).replace("\n", "")
		origHour = subprocess.check_output(["exiftool", "-d", "%H", "-"+refExifTag, "-s3", options.ref_file]).replace("\n", "")
		origMinute = subprocess.check_output(["exiftool", "-d", "%M", "-"+refExifTag, "-s3", options.ref_file]).replace("\n", "")
		origSecond = subprocess.check_output(["exiftool", "-d", "%S", "-"+refExifTag, "-s3", options.ref_file]).replace("\n", "")
	
		origTime = time.strptime(origYear+origMonth+origDay+origHour+origMinute+origSecond, "%Y%m%d%H%M%S")
		origTimeSeconds = time.mktime(origTime)
	
		refYear = options.ref_year if options.ref_year else origYear
		refMonth = options.ref_month if options.ref_month else origMonth
		refDay = options.ref_day if options.ref_day else origDay
		refHour = options.ref_hour if options.ref_hour else origHour
		refMinute = options.ref_minute if options.ref_minute else origMinute
		refSecond = options.ref_second if options.ref_second else origSecond
	
		refTime = time.strptime(refYear+refMonth+refDay+refHour+refMinute+refSecond, "%Y%m%d%H%M%S")
		refTimeSeconds = time.mktime(refTime)
	
		shiftSeconds = refTimeSeconds - origTimeSeconds
		shiftString = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(shiftSeconds))
		shiftArg = "-AllDates+=\"0:0:0 0:0:"+str(shiftSeconds)+"\""
		print shiftSeconds, shiftString
	
		if shiftSeconds == 0:
			print "Times are equal. Nothing to do!"
			print ""
			parser.print_help()
			sys.exit(0)
	
		for inputFile in inputFiles:
			command = "exiftool -overwrite_original_in_place " + shiftArg +" "+ inputFile
			print command
			os.system(command)
	
	if options.check:
		inputFile1 = None
		inputFile2 = None
		dateSeconds1 = 0
		dateSeconds2 = 0
		
		for index, inputFile in enumerate(inputFiles):
			dateString = subprocess.check_output(["exiftool", "-d", "%Y%m%d%H%M%S", "-"+refExifTag, "-s3", inputFile]).replace("\n", "")
			dateSeconds = time.mktime(time.strptime(dateString, "%Y%m%d%H%M%S"))
			
			inputFile1 = inputFile2
			dateSeconds1 = dateSeconds2
			inputFile2 = inputFile
			dateSeconds2 = dateSeconds
				
			if dateSeconds2 < dateSeconds1:
				commands = map(lambda errorFile: "exiftool -s3 -"+refExifTag + " " + errorFile, [inputFile1, inputFile2])
				for command in commands:
					print command
					os.system(command)
					print ""

if __name__ == "__main__": main()

