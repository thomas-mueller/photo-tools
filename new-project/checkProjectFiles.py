#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import os
import pprint

import directorynames
import photoinfo


def check_incomplete_jpg_raw_pairs(project_dir, jpg_extensions=None, raw_extensions=None):

	# default arguments
	if jpg_extensions == None: jpg_extensions = ["jpg", "jpeg", "JPG", "JPEG"]
	if raw_extensions == None: raw_extensions = ["cr2", "CR2"]
	
	# extract all files to check
	jpgFiles = directorynames.flatglob([os.path.join(project_dir, "*."+extension) for extension in jpg_extensions])
	rawFiles = directorynames.flatglob([os.path.join(project_dir, "*."+extension) for extension in raw_extensions])
	
	# extract all creation dates
	files_by_date = {}
	for label, files in zip(["jpg", "raw"], [jpgFiles, rawFiles]):
		for image_file in files:
			date = photoinfo.load_exif_field(image_file, "-d", "%Y:%m:%d %H:%M:%S", "-DateTimeOriginal")
			files_by_date.setdefault(date, {}).setdefault(label, []).append(image_file)
	
	# filter for incomplete pais
	def filter_incomplete_paris(date_files_dict_pair):
		if "jpg" not in date_files_dict_pair[1]: return True
		if "raw" not in date_files_dict_pair[1]: return True
		if len(date_files_dict_pair[1]["jpg"]) != len(date_files_dict_pair[1]["raw"]): return True
		return False
	
	incomplete_pairs = dict(filter(lambda item: filter_incomplete_paris(item), files_by_date.items()))
	
	for date, files_dict in incomplete_pairs.items():
		jpg_files = files_dict.get("jpg", [])
		raw_files = files_dict.get("raw", [])
		if len(jpg_files) > 1 or len(raw_files) > 1:
			jpg_file_names = set([os.path.splitext(os.path.basename(image_file))[0] for image_file in jpg_files])
			raw_file_names = set([os.path.splitext(os.path.basename(image_file))[0] for image_file in raw_files])
			
			jpg_raw_differences = jpg_file_names.difference(raw_file_names)
			if len(jpg_raw_differences) == 0:
				del incomplete_pairs[date]["jpg"]
			else:
				for difference in jpg_raw_differences:
					incomplete_pairs[date]["jpg"] = filter(lambda image_file: difference in image_file, jpg_files)
			
			raw_jpg_differences = raw_file_names.difference(jpg_file_names)
			if len(raw_jpg_differences) == 0:
				del incomplete_pairs[date]["raw"]
			else:
				for difference in raw_jpg_differences:
					incomplete_pairs[date]["raw"] = filter(lambda image_file: difference in image_file, raw_files)
	
	# create symlinks to detected files
	subdir = "incomplete-jpg-raw-pairs"
	symlinks_dir = os.path.join(project_dir, subdir)
	if not os.path.exists(symlinks_dir):
		os.makedirs(symlinks_dir)
	
	n_inclomplete_pairs = 0
	for files_dict in incomplete_pairs.values():
		for image_files in files_dict.values():
			for image_file in image_files:
				target = os.path.join(symlinks_dir, os.path.basename(image_file))
				if not os.path.exists(target):
					os.symlink(os.path.relpath(image_file, symlinks_dir), target)
				n_inclomplete_pairs += 1
	
	if n_inclomplete_pairs == 0:
		print "No incomplete pairs of JPG/RAW files found."
	else:
		print n_inclomplete_pairs, "incomplete pairs of JPG/RAW files found. Symlinks to these files are created in \"%s\"." % symlinks_dir


def check_panos(project_dir):
	pass


def main():
	parser = argparse.ArgumentParser(description="Check files of new project.")

	parser.add_argument("project_path", help="Path to arbitrary directory of new project.")
	
	parser.add_argument("--check-incomplete-jpg-raw-pairs", default=True, action="store_true",
	                    help="Check incomplete pairs of JPG/RAW files. [Default: %(default)s]")
	parser.add_argument("--no-check-incomplete-jpg-raw-pairs", default=True, action="store_false",
	                    dest="check_incomplete_jpg_raw_pairs",
	                    help="Do not check incomplete pairs of JPG/RAW files.")
	
	parser.add_argument("--check-panos", default=True, action="store_true",
	                    help="Check possible panoramic files. [Default: %(default)s]")
	parser.add_argument("--no-check-panos", default=True, action="store_false",
	                    dest="check_panos",
	                    help="Do not check possible panoramic files.")
	
	args = parser.parse_args()
	
	# TODO: get all tmp directories
	project_tmp_dir_2d = args.project_path
	
	if args.check_incomplete_jpg_raw_pairs:
		check_incomplete_jpg_raw_pairs(project_tmp_dir_2d)
	
	if args.check_panos:
		check_panos(project_tmp_dir_2d)

if __name__ == "__main__":
	main()

