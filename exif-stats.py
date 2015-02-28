#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import numpy

import ROOT

import phototools
import progressiterator


def main():
	parser = argparse.ArgumentParser(description="Convert set of images into video.", parents=[logger.loggingParser])
	
	parser.add_argument("images", nargs="+",
	                    help="Image files.")
	parser.add_argument("-e", "--exif-tags", nargs="+", default=[],
	                    help="Exif tags to retrieve. [Default: %(default)s]")
	parser.add_argument("-r", "--reg-exps", nargs="+", default=[None],
	                    help="Regular expressions to retrieve values from exif infos. [Default: %(default)s]")
	parser.add_argument("-b", "--branch-names", nargs="+", default=[None],
	                    help="Names for branches. [Default: %(default)s]")
	parser.add_argument("-o", "--output", default="exif-stats.root",
	                    help="Output ROOT file. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	root_file = ROOT.TFile(args.output, "RECREATE")
	tree = ROOT.TTree("exif", "")
	
	values = []
	for branch_name in args.branch_names:
		values.append(numpy.zeros(1, dtype=float))
		tree.Branch(branch_name, values[-1], branch_name+"/D")
	
	for image in progressiterator.ProgressIterator(args.images, description="Processing images"):
		for index, (exif_tag, reg_exp) in enumerate(zip(args.exif_tags, args.reg_exps)):
			exif_result = phototools.load_exif_field(image, *["-d", "%Y:%m:%d %H:%M:%S", "-"+exif_tag])
			values[index][0] = float(exif_result.replace("mm", "").strip())
		tree.Fill()
	
	root_file.Write()
	log.info("Created tree \"exif\" in file \"%s\"." % args.output)

if __name__ == "__main__":
	main()

