#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import datetime
import os

import directorynames


def main():
	parser = argparse.ArgumentParser(description="Create a new photo project.")

	parser.add_argument("project_name", help="Name of new project.")
	
	parser.add_argument("--base-dir", default=".",
	                    help="Base directory which should contain at least a 2D subdirectory. [Default: %(default)s]")
	
	parser.add_argument("--dimensions", type=int, default=[2], nargs="+",
	                    help="Photo dimensions (2 or 3). [Default: %(default)s]")
	parser.add_argument("--year", type=int, default=datetime.date.today().year,
	                    help="Year for project. [Default: %(default)s]")
	parser.add_argument("--project-number", type=int, help="Number for project [Default: auto-determined].")

	parser.add_argument("--n-project-number-digits", type=int, default=2,
	                    help="Number of digits in string for project number. [Default: %(default)s]")
	
	args = parser.parse_args()
	
	if args.project_number == None:
		args.project_number = directorynames.determine_project_number(args.base_dir, args.year, args.project_name)
	
	tmp_dirs = [item for sub_list in [directorynames.get_subdirs(dimension, "tmp") for dimension in args.dimensions] for item in sub_list]
	tmp_dirs = [os.path.join(args.base_dir, subdir, str(args.year),
	                         directorynames.get_dirname(args.year, args.project_number, args.n_project_number_digits, args.project_name)) for subdir in tmp_dirs]

	for tmp_dir in tmp_dirs:
		if os.path.exists(tmp_dir):
			print tmp_dir, "exists already."
		else:
			#os.makedirs(tmp_dir)
			print tmp_dir, "created."
	print "Copy your files in these directories."


if __name__ == "__main__":
	main()

