#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import glob
import os

import filetools
import phototools
import progressiterator


def main():
	parser = argparse.ArgumentParser(description="Photo tools.", parents=[logger.loggingParser])
	
	parser.add_argument("-s", "--step", type=int, default=0,
	                    help="Step number. [Default: %(default)s]")
	parser.add_argument("-m", "--mode", default="2D", choices=["2D", "3D"],
	                    help="Mode. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	steps = {
		"2D" : [
			"move.py",
			"rename.py",
		],
		"3D" : [
		],
	}
	
	if (args.step > 0) and (args.step-1 < len(steps[args.mode])):
		log.info(steps[args.mode][args.step-1])
	else:
		log.info("Steps for %s mode:" % args.mode)
		for index, step in enumerate(steps[args.mode]):
			log.info("\t%2d. %s" % (index+1, step))


if __name__ == "__main__":
	main()

