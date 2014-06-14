#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import locale
import numpy
import os
import pprint
import scipy.cluster.hierarchy
import time

import directorynames
import photoinfo


def get_files_by_date_and_type(project_dir, types_dict=None):

	# default arguments
	if types_dict == None:
		types_dict = {
			"jpg" : ["jpg", "jpeg", "JPG", "JPEG"],
			"raw" : ["cr2", "CR2"],
		}
	
	files_by_date_and_type = {}
	for label, types in types_dict.items():
		for image_file in directorynames.flatglob([os.path.join(project_dir, "*."+image_type) for image_type in types]):
			date = photoinfo.load_exif_field(image_file, "-d", "%Y:%m:%d %H:%M:%S", "-DateTimeOriginal")
			if len(types_dict) == 1:
				files_by_date_and_type.setdefault(date, []).append(image_file)
			else:
				files_by_date_and_type.setdefault(date, {}).setdefault(label, []).append(image_file)
	
	return files_by_date_and_type


def check_incomplete_jpg_raw_pairs(project_dir):

	types_dict = {
		"jpg" : ["jpg", "jpeg", "JPG", "JPEG"],
		"raw" : ["cr2", "CR2"],
	}
	files_by_date_and_type = get_files_by_date_and_type(project_dir, types_dict)
	
	# filter for incomplete pais
	def filter_incomplete_paris(date_files_dict_pair):
		if "jpg" not in date_files_dict_pair[1]: return True
		if "raw" not in date_files_dict_pair[1]: return True
		if len(date_files_dict_pair[1]["jpg"]) != len(date_files_dict_pair[1]["raw"]): return True
		return False
	
	incomplete_pairs = dict(filter(lambda item: filter_incomplete_paris(item), files_by_date_and_type.items()))
	
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

	types_dict = {
		"all" : ["jpg", "jpeg", "JPG", "JPEG"]#, "cr2", "CR2"],
	}
	files_by_date = get_files_by_date_and_type(project_dir, types_dict)
	
	portrait_file_items = []
	for date, files in files_by_date.items():
		date_seconds = int(time.mktime(time.strptime(date, "%Y:%m:%d %H:%M:%S")))
		for image_file in files:
			dimensions = [int(item) for item in photoinfo.load_image_dimensions(image_file).split()]
			if dimensions[1] > dimensions[0]:
				portrait_file_items.append([date_seconds, image_file])
	portrait_file_items.sort(cmp=lambda a, b: a[0] - b[0] if a[0] - b[0] != 0 else locale.strcoll(a[1], b[1]))
	
	dates = numpy.array([[date] for date in zip(*portrait_file_items)[0]])
	cluster_indices = scipy.cluster.hierarchy.fclusterdata(dates, 1.0)
	portrait_file_items_clustered = {}
	for index, cluster_index in enumerate(cluster_indices):
		portrait_file_items_clustered.setdefault(cluster_index, []).append(portrait_file_items[index])
	
	portrait_files_clustered = sorted(portrait_file_items_clustered.values(), key=lambda item: item[0])
	
	# create symlinks to detected files
	subdir = "panos"
	symlinks_dir = os.path.join(project_dir, subdir)
	
	for index, cluster in enumerate(portrait_files_clustered):
		symlinks_cluster_dir = os.path.join(symlinks_dir, str(index))
		if not os.path.exists(symlinks_cluster_dir):
			os.makedirs(symlinks_cluster_dir)
		
		for file_item in cluster:
			target = os.path.join(symlinks_cluster_dir, os.path.basename(file_item[1]))
			if not os.path.exists(target):
				os.symlink(os.path.relpath(file_item[1], symlinks_cluster_dir), target)
	
	if len(portrait_files_clustered) == 0:
		print "No panoramas found."
	else:
		print len(portrait_files_clustered), "panoramas found. Symlinks to them are created in \"%s\"." % symlinks_dir


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

