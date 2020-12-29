#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import math
import os
import shlex
import shutil
import string

import progressiterator


def main():
	parser = argparse.ArgumentParser(description="Convert Geeqie collection into web gallery.", parents=[logger.loggingParser])
	
	parser.add_argument("-i", "--input", required=True,
	                    help="Input Geeqie collection file.")
	parser.add_argument("-o", "--output", required=True,
	                    help="Output directory.")
	parser.add_argument("-t", "--title",
	                    help="Title. [Default: name of input file]")
	parser.add_argument("-f", "--favicon",
	                    help="Favicon.")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	if not os.path.exists(args.output):
		os.makedirs(args.output)
	
	if args.title is None:
		args.title = os.path.splitext(os.path.basename(args.input))[0]
	
	input_files = []
	with open(args.input) as collection_file:
		for line in collection_file:
			line = line.strip()
			if line.startswith("\"") and line.endswith("\""):
				input_files.append(os.path.relpath(line.replace("\"", ""), "."))
	name_format = "image_%0" + str(int(math.floor(math.log10(len(input_files))))+1) + "d%s"
	
	images_html = ""
	template_image_html = string.Template("<div class=\"step slide photo\" data-x=\"$data_x\" data-y=\"0\" style=\"background-image:url($path);\"></div>")
	for index, input_file in enumerate(progressiterator.ProgressIterator(input_files, description="Copy and resize files")):
		output_file = os.path.join(args.output, name_format % (index+1, os.path.splitext(input_file)[-1]))
		logger.subprocessCall(shlex.split("convert %s -resize 1500x1000> %s" % (input_file, output_file)))
		
		image_html = template_image_html.safe_substitute(data_x=str(index*1600), path=os.path.basename(output_file))
		images_html += ("\n" + image_html)
	
	if args.favicon:
		shutil.copy(args.favicon, os.path.join(args.output, os.path.basename(args.favicon)))
	
	template_index_html = None
	with open(os.path.join(os.path.dirname(__file__), "template.index.html")) as template_index_html_file:
		template_index_html = string.Template(template_index_html_file.read())
	index_html = template_index_html.safe_substitute(images=images_html, title=args.title, favicon=os.path.join(args.output, os.path.basename(args.favicon)) if args.favicon else "")
	
	with open(os.path.join(args.output, "index.html"), "w") as index_html_file:
		index_html_file.write(index_html)


if __name__ == "__main__":
	main()

