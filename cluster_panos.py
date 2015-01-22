#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import numpy
import os
import re
import scipy.cluster.hierarchy

import filetools
import phototools
import progressiterator


def main():
	parser = argparse.ArgumentParser(description="Cluster panoramas from portrait-format photos.", parents=[logger.loggingParser])
	
	parser.add_argument("-j", "--jpg-dir", required=True,
	                    help="Directory containing JPG photos.")
	parser.add_argument("-r", "--raw-dir",
	                    help="Directory containing RAW photos.")
	parser.add_argument("-p", "--pano-dir", default="PANO",
	                    help="Subdirectory for panoramas. [Default: %(default)s]")
	parser.add_argument("-e", "--exif-date-tag", default="DateTimeOriginal",
	                    help="Exif tag for date of creation. [Default: %(default)s]")
	parser.add_argument("-n", "--name",
	                    help="Name for panorama directories.")
	parser.add_argument("--min-n-photos", default=3,
	                    help="Minimum number of photos in one panorama. [Default: %(default)s]")
	parser.add_argument("--dry-run", action="store_true", default=False,
	                    help="Testing mode without applying any changes to the files. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	jpg_files = filetools.get_files(args.jpg_dir, ["*"])
	raw_files = [] if args.raw_dir is None else filetools.get_files(args.raw_dir, ["*"])
	
	jpg_files_dates = phototools.FileDate.get_files_dates(jpg_files, args.exif_date_tag)
	raw_files_dates = phototools.FileDate.get_files_dates(raw_files, args.exif_date_tag)
	
	portrait_jpg_files_dates = filter(lambda file_date: phototools.is_portrait_format(file_date.file), progressiterator.ProgressIterator(jpg_files_dates, description="Read image dimensions"))
	portrait_jpg_files_dates.sort()
	
	cluster_data = numpy.array([[float(file_date.date), float(re.search(".*_(?P<file_number>\d*)\.\w*", os.path.basename(file_date.file)).groupdict()["file_number"])] for file_date in portrait_jpg_files_dates])
	cluster_indices = scipy.cluster.hierarchy.fclusterdata(cluster_data, 25.0, criterion="distance")
	
	clustered_jpg_files_dates = {}
	for index, cluster_index in enumerate(cluster_indices):
		clustered_jpg_files_dates.setdefault(cluster_index, []).append(portrait_jpg_files_dates[index])
	clustered_jpg_files_dates = [cluster for cluster in clustered_jpg_files_dates.values() if len(cluster) >= args.min_n_photos]
	clustered_jpg_files_dates.sort(key=lambda cluster: cluster[0].file)
	
	for index, jpg_files_dates_cluster in enumerate(progressiterator.ProgressIterator(clustered_jpg_files_dates, description="Move candidates of panoramic photos to subdirectories")):
		raw_files_dates_cluster = [raw_files_dates[raw_files_dates.index(jpg_file_date)] for jpg_file_date in jpg_files_dates_cluster if jpg_file_date in raw_files_dates]
		
		pano_sub_dir = os.path.join(args.pano_dir, ("%s_" % args.name if args.name else "") + str(index+1))
		
		jpg_sub_dir = os.path.join(args.jpg_dir, pano_sub_dir)
		raw_sub_dir = os.path.join(args.raw_dir, pano_sub_dir)
		if (not args.dry_run) and (not os.path.exists(jpg_sub_dir)):
			os.makedirs(jpg_sub_dir)
		if (not args.dry_run) and (len(raw_files_dates_cluster) > 0) and (not os.path.exists(raw_sub_dir)):
			os.makedirs(raw_sub_dir)
		
		for file_date in jpg_files_dates_cluster + raw_files_dates_cluster:
			new_file = os.path.join(os.path.dirname(file_date.file), pano_sub_dir, os.path.basename(file_date.file))
			if args.dry_run:
				log.info("mv %s %s" % (file_date.file, new_file))
			else:
				os.rename(file_date.file, new_file)


if __name__ == "__main__":
	main()

