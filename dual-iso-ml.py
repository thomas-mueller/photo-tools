#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import glob
import os
import shlex

import phototools
import progressiterator
import tools


def main():
	parser = argparse.ArgumentParser(description="Post-process dual ISO images with Magic Lantern.", parents=[logger.loggingParser])
	
	parser.add_argument("images", nargs="+",
	                    help="Image files or directories.")
	parser.add_argument("--cr2hdr", default="$HOME/magic-lantern/modules/dual_iso/cr2hdr",
	                    help="Executable cr2hdr. [Default: %(default)s]")
	parser.add_argument("--raw-ext", nargs="+", default=["cr2", "CR2"],
	                    help="RAW file extensions. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	args.cr2hdr = os.path.expandvars(args.cr2hdr)
	
	images = tools.flatten(
			[tools.flatten([glob.glob(os.path.join(arg, "*."+ext)) for ext in args.raw_ext])
			 if os.path.isdir(arg)
			 else [arg]
			 for arg in args.images]
	)
	
	"""
	images_isos = [
			(image, phototools.load_exif_field(image, "-ISO"), phototools.load_exif_field(image, "-AutoISO"))
			for image in progressiterator.ProgressIterator(images, description="Load EXIF ISO infos")
	]
	
	dual_iso_images = [image for image, iso, auto_iso in images_isos if iso != auto_iso]
	"""
	dual_iso_images = images
	
	for image in progressiterator.ProgressIterator(dual_iso_images, description="Post-process dual ISO images"):
		command = "%s %s" % (args.cr2hdr, image)
		log.debug(command)
		logger.subprocessCall(command)


if __name__ == "__main__":
	main()

