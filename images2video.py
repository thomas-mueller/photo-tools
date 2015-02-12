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
	parser = argparse.ArgumentParser(description="Convert set of images into video.", parents=[logger.loggingParser])
	
	parser.add_argument("-i", "--images", nargs="+",
	                    help="Image files.")
	parser.add_argument("-o", "--output", default="output.mp4",
	                    help="Output video file. [Default: %(default)s]")
	parser.add_argument("-r", "--resolution", nargs=2, default=[1280, 720], type=int,
	                    help="Video resolution. [Default: %(default)s]")
	parser.add_argument("-f", "--frame-rate", default=25.0, type=float,
	                    help="Video frame rate. [Default: %(default)s]")
	parser.add_argument("-d", "--image-durations", nargs="+", default=[5.0], type=float,
	                    help="Image slide durations in seconds. [Default: %(default)s]")
	parser.add_argument("-t", "--transition-times", nargs="+", default=[1.0], type=float,
	                    help="Transition times in seconds. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	multivision = multivisiontools.Multivision(
			frame_rate = args.frame_rate,
			resolution = args.resolution,
			video_format = os.path.splitext(args.output)[-1]
	)
	
	output = multivision.images_to_video(
			args.images,
			video_file = args.output,
			image_durations = args.image_durations,
			transition_times = args.transition_times
	)
	
	log.info("Created video in \"%s\" from %d images." % (args.output, len(args.images)))

if __name__ == "__main__":
	main()

