#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import math
import os
import shutil

import multivisiontools


def main():
	parser = argparse.ArgumentParser(description="Convert Geeqie collection into video.", parents=[logger.loggingParser])
	
	parser.add_argument("-i", "--input", nargs="+", #required=True,
	                    help="Input Geeqie collection file.")
	parser.add_argument("-o", "--output", required=True,
	                    help="Output video file.")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	multivisiontools.Multivision(resolution=(480, 320)).images_to_video(args.input, video_file=args.output)

if __name__ == "__main__":
	main()

