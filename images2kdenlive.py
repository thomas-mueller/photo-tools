#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse

import kdenlivetools


def main():
	parser = argparse.ArgumentParser(description="Convert set of images into Kdenlive project.",
	                                 parents=[logger.loggingParser])
	
	parser.add_argument("-k", "--kdenlive-template", required=True,
	                    help="Kdenlive template project file.")
	parser.add_argument("-i", "--images", nargs="+",
	                    help="Image files.")
	parser.add_argument("-o", "--output", default="project.kdenlive",
	                    help="Output Kdenlive project file. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	kdenliveProject = kdenlivetools.KdenliveProject(args.kdenlive_template)
	
	kdenliveProject.save(args.output)
	log.info("Created Kdenlive project \"%s\" from %d images." % (args.output, len(args.images)))
	

if __name__ == "__main__":
	main()

