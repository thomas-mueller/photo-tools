
# -*- coding: utf-8 -*-

import glob
import locale
import os
import re
import time

import progressmonitor
import photoinfo


def flatglob(paths):
	if isinstance(paths, basestring):
		paths = [paths]
	return [item for sub_list in [glob.glob(path) for path in paths] for item in sub_list]

def get_subdirs(dimension, uses):
	if isinstance(uses, basestring):
		uses = [uses]
	subdirs = []
	for use in uses:
		if dimension == 2:
			subdir = "2D"
			if use == "tmp": subdirs.append(os.path.join(subdir, "TMP"))
			elif use == "jpg": subdirs.append(os.path.join(subdir, "JPG"))
			elif use == "raw": subdirs.append( os.path.join(subdir, "RAW"))
			elif use == "raw2jpg": subdirs.append(os.path.join(subdir, "RAW2JPG"))
			elif use == "mov": subdirs.append(os.path.join(subdir, "MOV"))
			elif use == "pano": subdirs.append(os.path.join(subdir, "PANO"))
		elif dimension == 3:
			subdir = "3D"
			if use == "3d": subdirs.append(os.path.join(subdir, "3D"))
			if use == "l" or use == "tmp": subdirs.append(os.path.join(subdir, "L"))
			if use == "r" or use == "tmp": subdirs.append(os.path.join(subdir, "R"))
	return subdirs


def parse_directory_structure(base_dir, year):
	search_sub_dirs = get_subdirs(2, ["tmp", "jpg", "raw", "mov", "pano"])+get_subdirs(3, ["tmp", "3d", "l", "r"])
	search_sub_dirs = [os.path.join(base_dir, subdir, str(year), "*") for subdir in search_sub_dirs]
	search_sub_dirs = flatglob(search_sub_dirs)
	parsed_directory_structure = {}
	for search_sub_dir in search_sub_dirs:
		parsed_subdir = re.match(".*/(?P<year>\d*)_(?P<project_number>\d*)_(?P<project_name>[^/]*)", search_sub_dir).groupdict()
		parsed_directory_structure[parsed_subdir["project_name"]] = int(parsed_subdir["project_number"])
	return parsed_directory_structure


def determine_project_number(base_dir, year, project_name):
	parsed_directory_structure = parse_directory_structure(base_dir, year)
	project_number = parsed_directory_structure.get(project_name, max(parsed_directory_structure.values()+[0])+1)
	return project_number


def get_number_string(number, n_digits):
	return ("%s0%dd" % ("%", n_digits)) % number


def get_dirname(year, project_number, n_project_number_digits, project_name):
	return str(year)+"_"+get_number_string(project_number, n_project_number_digits)+"_"+project_name


def get_files_by_date_and_type(project_dirs, types_dict=None):

	# (default) parameters
	if isinstance(project_dirs, basestring):
		project_dirs = [project_dirs]
	if types_dict == None:
		types_dict = {
			"jpg" : ["jpg", "jpeg", "JPG", "JPEG"],
			"raw" : ["cr2", "CR2"],
		}
	
	files_by_date_and_type = {}
	for project_dir in project_dirs:
		for label, types in types_dict.items():
			image_files = flatglob([os.path.join(project_dir, "*."+image_type) for image_type in types])
			progress_monitor = progressmonitor.ProgressMonitor(len(image_files))
			print "Loading dates for %s files in directory \"%s\"..." % (label, project_dir)
			for image_file in image_files:
				progress_monitor.next()
				date = photoinfo.load_exif_field(image_file, "-d", "%Y:%m:%d %H:%M:%S", "-DateTimeOriginal")
				date_seconds = int(time.mktime(time.strptime(date, "%Y:%m:%d %H:%M:%S")))
				if len(types_dict) == 1:
					files_by_date_and_type.setdefault(date_seconds, []).append(image_file)
				else:
					files_by_date_and_type.setdefault(date_seconds, {}).setdefault(label, []).append(image_file)
			print ""
	return files_by_date_and_type


def get_sorted_jpg_raw_pairs(project_dirs, jpg_extensions=None, raw_extensions=None):

	# (default) parameters
	if isinstance(project_dirs, basestring):
		project_dirs = [project_dirs]
	if jpg_extensions == None:
		jpg_extensions = ["jpg", "jpeg", "JPG", "JPEG"]
	if raw_extensions == None:
		raw_extensions = ["cr2", "CR2"]

	types_dict = {
		"jpg" : jpg_extensions,
		"raw" : raw_extensions,
	}
	
	files_by_date_and_type = get_files_by_date_and_type(project_dirs, types_dict=types_dict)
	
	jpg_raw_pairs = []
	for date in sorted(files_by_date_and_type.keys()):
		jpg_files = files_by_date_and_type[date].get("jpg", [])
		raw_files = files_by_date_and_type[date].get("raw", [])
		
		if len(jpg_files) <= 1 and len(raw_files) <= 1:
			jpg_raw_pairs.append([jpg_files[0] if len(jpg_files) > 0 else None,
			                      raw_files[0] if len(raw_files) > 0 else None])
		else:
			jpg_file_names = [os.path.splitext(os.path.basename(image_file))[0] for image_file in jpg_files]
			raw_file_names = [os.path.splitext(os.path.basename(image_file))[0] for image_file in raw_files]
			
			all_file_names = list(set(jpg_file_names).union(set(raw_file_names)))
			for file_name in sorted(all_file_names, cmp=locale.strcoll):
				jpg_raw_pairs.append([jpg_files[jpg_file_names.index(file_name)] if file_name in jpg_file_names else None,
				                      raw_files[raw_file_names.index(file_name)] if file_name in raw_file_names else None])
	
	return jpg_raw_pairs

