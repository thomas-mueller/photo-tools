#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import glob
import os

import filetools
import phototools
import progressiterator


def main():
	parser = argparse.ArgumentParser(description="Set up directory structure for 2D photos.", parents=[logger.loggingParser])
	
	parser.add_argument("project_dir",
	                    help="Project directory containing photo/movie files")
	
	parser.add_argument("-j", "--jpg-dir", default="JPG",
	                    help="Subdirectory name for the JPG photos. [Default: %(default)s]")
	parser.add_argument("-r", "--raw-dir", default="RAW",
	                    help="Subdirectory name for the RAW photos. [Default: %(default)s]")
	parser.add_argument("-m", "--mov-dir", default="MOV",
	                    help="Subdirectory name for the movies. [Default: %(default)s]")
	
	parser.add_argument("--jpg-ext", nargs="+", default=["jpg", "jpeg", "JPG", "JPEG"],
	                    help="JPG file extensions. [Default: %(default)s]")
	parser.add_argument("--raw-ext", nargs="+", default=["cr2", "CR2"],
	                    help="RAW file extensions. [Default: %(default)s]")
	parser.add_argument("--mov-ext", nargs="+", default=["mov", "mpeg", "mp4", "MOV", "MPEG", "MP4"],
	                    help="MOV file extensions. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	args = vars(args)
	
	for file_type in ["JPG", "RAW", "MOV"]:
		files = filetools.get_files(args["project_dir"], args["%s_ext" % file_type.lower()])
		
		sub_dir = os.path.join(args["project_dir"], args["%s_dir" % file_type.lower()])
		if (len(files) > 0) and (not os.path.exists(sub_dir)):
			os.makedirs(sub_dir)
		for file in progressiterator.ProgressIterator(files, description="Move %s files" % file_type):
			os.rename(file, os.path.join(sub_dir, os.path.basename(file)))


if __name__ == "__main__":
	main()

