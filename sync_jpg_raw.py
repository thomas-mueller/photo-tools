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
	parser = argparse.ArgumentParser(description="Synchronise JPG and RAW photos, including options to remove supernumerous files.", parents=[logger.loggingParser])
	
	parser.add_argument("-j", "--jpg-dir", required=True,
	                    help="Directory containing JPG photos.")
	parser.add_argument("-r", "--raw-dir", required=True,
	                    help="Directory containing RAW photos.")
	parser.add_argument("-e", "--exif-date-tag", default="DateTimeOriginal",
	                    help="Exif tag for date of creation. [Default: %(default)s]")
	parser.add_argument("-m", "--modes", default=["print"], action="append",
	                    choices=["print", "rm_jpg", "rm_raw"],
	                    help="Modes. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	jpg_files = filetools.get_files(args.jpg_dir, ["*"])
	raw_files = filetools.get_files(args.raw_dir, ["*"])
	
	jpg_files_dates = phototools.FileDate.get_files_dates(jpg_files, args.exif_date_tag)
	raw_files_dates = phototools.FileDate.get_files_dates(raw_files, args.exif_date_tag)
	
	jpg_files_dates.sort()
	raw_files_dates.sort()
	
	jpg_index, only_jpg_files = 0, []
	raw_index, only_raw_files = 0, []
	while jpg_index < len(jpg_files_dates) and raw_index < len(raw_files_dates):
		if jpg_files_dates[jpg_index] == raw_files_dates[raw_index]:
			jpg_index += 1
			raw_index += 1
		elif jpg_files_dates[jpg_index].date < raw_files_dates[raw_index].date:
			only_jpg_files.append(jpg_files_dates[jpg_index].file)
			jpg_index += 1
		else:
			only_raw_files.append(raw_files_dates[raw_index].file)
			raw_index += 1
	
	if "print" in args.modes:
		for file in only_jpg_files + only_raw_files:
			log.info(file)
	if "rm_jpg" in args.modes:
		for file in progressiterator(only_jpg_files, description="Remove supernumerous JPG files"):
			os.remove(file)
	if "rm_raw" in args.modes:
		for file in progressiterator(only_raw_files, description="Remove supernumerous RAW files"):
			os.remove(file)


if __name__ == "__main__":
	main()

