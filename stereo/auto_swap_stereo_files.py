#! /usr/bin/env python

from optparse import OptionParser
import glob, os, subprocess, sys



###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options]",
			              description="Swap left and right photo if EXIF orientation indicates wrong rotation of the camera")
	
	parser.add_option("-l", "--left", help="Input file or directory for left photos")
	parser.add_option("-r", "--right", help="Input file or directory for right photos")

	(options, args) = parser.parse_args()
	
	if not options.left or not options.right:
		print "ERROR: no inputs specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if (os.path.isfile(options.left) and not os.path.isfile(options.right)) or os.path.isdir(options.left) and not os.path.isdir(options.right):
		print "ERROR: both inputs must have the same type!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	filesLeft = glob.glob(os.path.join(options.left, "*")) if os.path.isdir(options.left) else [options.left]
	filesRight = glob.glob(os.path.join(options.right, "*")) if os.path.isdir(options.right) else [options.right]
	
	filesLeft.sort()
	filesRight.sort()
	
	filesZip = zip(filesLeft, filesRight)
	for index, files in enumerate(filesZip):
		fileLeft = files[0]
		fileRight = files[1]
		
		print "Image", index+1, "of", len(filesZip), "..."
		
		orientationLeft = subprocess.check_output(["exiftool", "-Orientation", "-s3", fileLeft]).replace("\n", "")
		orientationRight = subprocess.check_output(["exiftool", "-Orientation", "-s3", fileRight]).replace("\n", "")
		
		if "Horizontal (normal)" in orientationLeft and "Rotate 180" in orientationRight:
			os.system("mv -v %s %s" % (fileLeft, fileLeft+"~"))
			os.system("mv -v %s %s" % (fileRight, fileLeft))
			os.system("mv -v %s %s" % (fileLeft+"~", fileRight))

if __name__ == "__main__": main()

