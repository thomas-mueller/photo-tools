
import glob
import os
import re


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
	search_sub_dirs = [item for sub_list in [glob.glob(subdir) for subdir in search_sub_dirs] for item in sub_list]
	parsed_directory_structure = {}
	for search_sub_dir in search_sub_dirs:
		parsed_subdir = re.match(".*/(?P<year>\d*)_(?P<project_number>\d*)_(?P<project_name>[^/]*)", search_sub_dir).groupdict()
		parsed_directory_structure[parsed_subdir["project_name"]] = int(parsed_subdir["project_number"])
	return parsed_directory_structure


def determine_project_number(base_dir, year, project_name):
	parsed_directory_structure = parse_directory_structure(base_dir, year)
	project_number = parsed_directory_structure.get(project_name, max(parsed_directory_structure.values()+[0])+1)
	return project_number

def get_dirname(year, project_number, n_project_number_digits, project_name):
	return str(year)+"_"+(("%s0%dd" % ("%", n_project_number_digits)) % project_number)+"_"+project_name
