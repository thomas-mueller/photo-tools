#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import os

import directorynames


def prepare_incomplete_jpg_raw_pairs(input_dir, output_subdir):
	
	jpg_extensions = ["jpg", "jpeg", "JPG", "JPEG"]
	raw_extensions = ["cr2", "CR2"]
	
	jpg_raw_pairs = directorynames.get_sorted_jpg_raw_pairs(input_dir,
	                                                        jpg_extensions=jpg_extensions,
	                                                        raw_extensions=raw_extensions)
	
	# filter for incomplete pairs
	incomplete_pairs = filter(lambda pair: any([item == None for item in pair]), jpg_raw_pairs)
	single_items = [pair[0] if pair[0] != None else pair[1] for pair in incomplete_pairs]
	
	# create symlinks to detected files
	symlinks_dir = os.path.join(input_dir, output_subdir)
	if not os.path.exists(symlinks_dir):
		os.makedirs(symlinks_dir)
	
	for image_file in single_items:
		target = os.path.join(symlinks_dir, os.path.basename(image_file))
		if not os.path.exists(target):
			os.symlink(os.path.relpath(image_file, symlinks_dir), target)
	
	if len(single_items) == 0:
		print "No incomplete pairs of JPG/RAW files found."
	else:
		print len(single_items), "incomplete pairs of JPG/RAW files found. Symlinks to these files are created in \"%s\"." % symlinks_dir


def complete_incomplete_jpg_raw_pairs(input_dir, output_subdir, delete_modus):
	symlinks_dir = os.path.join(input_dir, output_subdir)
	if not os.path.exists(symlinks_dir):
		print "Directory \"%s\" does not exist. Use modus 1 first." % symlinks_dir
		return

	files_to_delete = filter(lambda file_to_delete: os.path.islink(file_to_delete), glob.glob(os.path.join(symlinks_dir, "*.*")))
	files_to_delete = [os.path.realpath(file_to_delete) for file_to_delete in files_to_delete]
	
	if len(files_to_delete) > 0:
		files_to_delete_string = " ".join(["\"%s\"" % file_to_delete for file_to_delete in files_to_delete])

		if delete_modus == None:
			os.system("rm -i %s" % files_to_delete_string)
		elif delete_modus == False:
			os.system("trash-put %s" % files_to_delete_string)
		else:
			os.system("rm -v %s" % files_to_delete_string)
	
	os.system("rm -rf %s" % symlinks_dir)


def main():
	parser = argparse.ArgumentParser(description="Check for incomplete pairs of JPG/RAW photos.")

	parser.add_argument("input_dirs", nargs="+",
	                    help="Paths to arbitrary directories of new project.")
	
	modusArguments = parser.add_mutually_exclusive_group()
	modusArguments.add_argument("-1", "--preparation", default=True, action="store_true",
	                            help="Preparation modus. In this modus no existing files are modified. [Default modus]")
	modusArguments.add_argument("-2", "--completion", default=True, action="store_false", dest="preparation",
	                            help="Completion modus. In this modus files can be deleted.")
	
	deletionModusArguments = parser.add_mutually_exclusive_group()
	deletionModusArguments.add_argument("-t", "--delete-move-to-trash", default=None, action="store_false", dest="delete_modus",
	                                    help="Delete files linked to output directory by moving to trash directory in modus 2.")
	deletionModusArguments.add_argument("-d", "--delete-without-prompt", default=None, action="store_true", dest="delete_modus",
	                                    help="Delete files linked to output directory without prompt in modus 2.")
	
	parser.add_argument("-o", "--output-subdir", default="incomplete-jpg-raw-pairs-to-delete",
	                    help="Name of the subdirectory where to put symlinks to and from where to delete incomplete pairs. [Default: %(default)s]")
	
	args = parser.parse_args()
	
	for input_dir in args.input_dirs:
		if args.preparation:
			prepare_incomplete_jpg_raw_pairs(input_dir, args.output_subdir)
		else:
			complete_incomplete_jpg_raw_pairs(input_dir, args.output_subdir, args.delete_modus)


if __name__ == "__main__":
	main()

