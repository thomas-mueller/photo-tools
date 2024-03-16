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
import tqdm


def main():
	parser = argparse.ArgumentParser(description="Rename set of photos.", parents=[logger.loggingParser])
	
	parser.add_argument("-j", "--jpg-dir", required=True,
	                    help="Directory containing JPG photos.")
	parser.add_argument("--jpg-ext", nargs="+", default=["jpg", "jpeg", "JPG", "JPEG"],
	                    help="JPG file extensions. [Default: %(default)s]")
	parser.add_argument("-r", "--raw-dir",
	                    help="Directory containing RAW photos.")
	parser.add_argument("--raw-ext", nargs="+", default=["cr2", "CR2", "arw", "ARW", "dng", "DNG"],
	                    help="RAW file extensions. [Default: %(default)s]")
	parser.add_argument("-e", "--exif-date-tag", default="DateTimeOriginal",
	                    help="Exif tag for date of creation. [Default: %(default)s]")
	parser.add_argument("-n", "--name", required=True,
	                    help="File name prefix.")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	jpg_files = filetools.get_files(args.jpg_dir, args.jpg_ext)
	raw_files = [] if args.raw_dir is None else filetools.get_files(args.raw_dir, args.raw_ext)

	files_dates = []
	for files in [jpg_files, raw_files]:
		files_dates.extend(phototools.FileDate.get_files_dates(files, args.exif_date_tag))
	files_dates.sort()
	
	rename_files = phototools.FileDate.rename_files(files_dates, args.name)
	for original_file, new_file in tqdm.tqdm(rename_files, desc="Rename files"):
		os.rename(original_file, new_file)


if __name__ == "__main__":
	main()

