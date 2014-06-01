#! /usr/bin/env python

from optparse import OptionParser
import copy, glob, os, subprocess, sys, time



###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options] <DIRECTORY1 | FILE1> <DIRECTORY2 | FILE2>",
			              description="Compare focal lenght of two pictures (either directly specified or all pairs of pictures in two directories). If they do not match each other, crop image with smaller focal lenght and resize both to the same size")

	parser.add_option("--scale-up-cropped", action="store_true", default=False, help="Scale up cropped image instead of scaling down non-cropped image. [Default: False]")
	parser.add_option("--overwrite", action="store_true", default=False, help="Overwrite original files. [Default: False]")

	(options, args) = parser.parse_args()
	
	if len(args) < 2:
		print "ERROR: no inputs specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if (os.path.isfile(args[0]) and not os.path.isfile(args[1])) or os.path.isdir(args[0]) and not os.path.isdir(args[1]):
		print "ERROR: both inputs must have the same type!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	files1 = glob.glob(os.path.join(args[0], "*")) if os.path.isdir(args[0]) else [args[0]]
	files2 = glob.glob(os.path.join(args[1], "*")) if os.path.isdir(args[1]) else [args[1]]
	
	files1.sort()
	files2.sort()
	
	filesZip = zip(files1, files2)
	for index, files in enumerate(filesZip):
		file1 = files[0]
		file2 = files[1]
		
		print "Image", index+1, "of", len(filesZip), "..."
		
		focalLenght1 = float(subprocess.check_output(["exiftool", "-FocalLength", "-s3", file1]).replace("\n", "").replace("mm", "").strip())
		focalLenght2 = float(subprocess.check_output(["exiftool", "-FocalLength", "-s3", file2]).replace("\n", "").replace("mm", "").strip())
		
		ratio = focalLenght1 / focalLenght2
		if ratio != 1.0:
		
			if not options.overwrite:
				os.system("cp %s %s" % (file1, file1.replace(".JPG", "_original.JPG").replace(".jpg", "_original.jpg")))
				os.system("cp %s %s" % (file2, file2.replace(".JPG", "_original.JPG").replace(".jpg", "_original.jpg")))
			
			if ratio < 1.0:
				fileLarge = file1
				fileSmall = file2
			else:
				ratio = 1.0 / ratio
				fileLarge = file2
				fileSmall = file1
			
			commands = [r"convert %s -gravity Center -crop %f%s%s %s" % (fileLarge, ratio*100.0, "%", ((" -resize %f%s" % (100.0/ratio, "%")) if options.scale_up_cropped else ""), fileLarge)]
			if not options.scale_up_cropped: commands.append(r"convert %s -resize %f%s %s" % (fileSmall, ratio*100.0, "%", fileSmall))
			
			for command in commands:
				print command
				os.system(command)

if __name__ == "__main__": main()

