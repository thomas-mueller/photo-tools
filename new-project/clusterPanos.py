#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import locale
import numpy
import os
import pprint
import re
import scipy.cluster.hierarchy
import time

import directorynames
import photoinfo
import progressmonitor


def cluster_panos(input_dir, output_subdir, types):
	
	types_dict = {
		"jpg" : types,
	}
	files_by_date = directorynames.get_files_by_date_and_type(input_dir, types_dict=types_dict)
	
	portrait_file_items = []
	progress_monitor = progressmonitor.ProgressMonitor(len(files_by_date))
	print "Loading image dimensions..."
	for date, files in files_by_date.items():
		progress_monitor.next()
		for image_file in files:
			dimensions = [int(item) for item in photoinfo.load_image_dimensions(image_file).split()]
			if dimensions[1] > dimensions[0]:
				portrait_file_items.append([date, image_file])
	print ""
	portrait_file_items.sort(cmp=lambda a, b: a[0] - b[0] if a[0] - b[0] != 0 else locale.strcoll(a[1], b[1]))
	
	print "Clustering portrait photos..."
	dates = numpy.array([[float(file_item[0]), float(re.search(".*_(?P<file_number>\d*)\.\w*", file_item[1]).groupdict()["file_number"])] for file_item in portrait_file_items])
	cluster_indices = scipy.cluster.hierarchy.fclusterdata(dates, 25.0, criterion="distance")
	portrait_file_items_clustered = {}
	for index, cluster_index in enumerate(cluster_indices):
		portrait_file_items_clustered.setdefault(cluster_index, []).append(portrait_file_items[index])
	
	portrait_files_clustered = sorted(portrait_file_items_clustered.values(), key=lambda item: item[0])
	portrait_files_clustered = filter(lambda item: len(item[1]) > 1, portrait_files_clustered)
	
	# create symlinks to detected files
	symlinks_dir = os.path.join(input_dir, output_subdir)
	
	for index, cluster in enumerate(portrait_files_clustered):
		symlinks_cluster_dir = os.path.join(symlinks_dir, directorynames.get_number_string(index+1, 3))
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
	parser = argparse.ArgumentParser(description="Try to find clusters of panoramas in new project.")

	parser.add_argument("input_dirs", nargs="+",
	                    help="Paths to arbitrary directories of new project.")
	
	parser.add_argument("-o", "--output-subdir", default="panos",
	                    help="Name of the subdirectory where to put symlinks to the pano clusters. [Default: %(default)s]")
	parser.add_argument("-t", "--types", default=["jpg", "jpeg", "JPG", "JPEG"], nargs="+",
	                    help="Types/extensions of files to consider. [Default: %(default)s]")
	
	args = parser.parse_args()
	
	for input_dir in args.input_dirs:
		cluster_panos(input_dir, args.output_subdir, args.types)


if __name__ == "__main__":
	main()

