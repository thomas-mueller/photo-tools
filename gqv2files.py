#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import math
import os
import shutil

#import progressiterator


def main():
	parser = argparse.ArgumentParser(description="Convert Geeqie collection into direcoty containing the files.", parents=[logger.loggingParser])
	
	parser.add_argument("-i", "--input", required=True,
	                    help="Input Geeqie collection file.")
	parser.add_argument("-o", "--output", required=True,
	                    help="Output directory.")
	parser.add_argument("--copy", action="store_true", default=False,
	                    help="Copy files instead of creating symlinks.")
	parser.add_argument("-n", "--name",
	                    help="Prefix name of the files. [Default: name of input file]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	if not os.path.exists(args.output):
		os.makedirs(args.output)
	
	if args.name is None:
		args.name = os.path.splitext(os.path.basename(args.input))[0]
	
	input_files = []
	with open(args.input) as collection_file:
		for line in collection_file:
			line = line.strip()
			if line.startswith("\"") and line.endswith("\""):
				input_files.append(line.replace("\"", ""))
	
	name_format = args.name + "_%0" + str(int(math.floor(math.log10(len(input_files))))+1) + "d%s"
	
	for index, input_file in enumerate(input_files):
		output_file = os.path.join(args.output, name_format % (index+1, os.path.splitext(input_file)[-1]))
		if args.copy:
			shutil.copy(input_file, output_file)
		else:
			input_file = os.path.relpath(input_file, os.path.dirname(output_file))
			os.symlink(input_file, output_file)


if __name__ == "__main__":
	main()

