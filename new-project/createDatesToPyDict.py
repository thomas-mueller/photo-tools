#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import time

import directorynames
import progressmonitor


def main():
	parser = argparse.ArgumentParser(description="Extract dates from files and store them in a python dictionary.")

	parser.add_argument("input", help="Input files or directories.", nargs="+")
	parser.add_argument("-o", "--output", default="createdates.py",
	                    help="Output python file. [Default: %(default)s]")
	parser.add_argument("-e", "--exif-tag", default="DateTimeOriginal",
	                    help="Exif tag for date of creation. [Default: %(default)s]")
	
	args = parser.parse_args()
	
	args.input = [os.path.join(item, "*") if os.path.isdir(item) else item for item in args.input]
	args.input = list(set(directorynames.flatglob(args.input)))
	
	date_format = "%Y:%m:%d %H:%M:%S"
	
	create_dates = {}
	progress = progressmonitor.ProgressMonitor(len(args.input))
	for input_file in args.input:
		date_string = subprocess.check_output(["exiftool", "-d", date_format, "-"+args.exif_tag, "-s3", input_file]).replace("\n", "")
		date_seconds = time.mktime(time.strptime(date_string, date_format))
		file_name, file_extension = os.path.splitext(input_file)
		create_dates.setdefault(date_seconds, {}).setdefault(file_extension, []).append(os.path.abspath(input_file))
		progress.next()
	print

	with open(args.output, "w") as output_file:
		output_file.write("create_dates = "+str(create_dates)+"\n")
		print args.output, "saved."
	
	#import imp
	#create_dates_module = imp.load_source("create_dates_module", args.output)
	#print create_dates_module.create_dates

if __name__ == "__main__":
	main()

