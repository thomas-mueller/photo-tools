#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import numpy
import os
from PIL import Image, ImageChops
import shutil


def get_ratio_images(image1, image2):
	ratio_data = []
	for index, (pixel1, pixel2) in enumerate(zip(list(image1.getdata()), list(image2.getdata()))):
		if type(pixel1) == tuple:
			ratio_pixel = []
			for band1, band2 in zip(pixel1, pixel2):
				sum_bands = band1 + band2
				ratio_band = int(255.0 * ((float(band1) / float(sum_bands)) if sum_bands > 0 else 0.5))
				ratio_pixel.append(ratio_band)
			ratio_data.append(tuple(ratio_pixel))
		else:
			band1, band2 = pixel1, pixel2
			sum_bands = band1 + band2
			ratio_band = int(255.0 * ((float(band1) / float(sum_bands)) if sum_bands > 0 else 0.5))
			ratio_data.append(ratio_band)
	
	ratio_data_array = numpy.reshape(numpy.array(ratio_data, dtype=numpy.uint8), tuple(list(image1.size)[::-1]+([len(ratio_data[0])] if type(ratio_data[0])==tuple else [])))
	ratio_image = Image.fromarray(ratio_data_array, mode=image1.mode)
	return ratio_image

def save_image(image, filename):
	image.save(filename)
	log.info("Saved image \"{image}\".".format(image=filename))


def main():
	parser = argparse.ArgumentParser(description="Stereo Reconstrucion.", parents=[logger.loggingParser])
	
	parser.add_argument("-l", "--input-left",
	                    help="Left input image. [Default: %(default)s]")
	parser.add_argument("-r", "--input-right",
	                    help="Right input image. [Default: %(default)s]")
	parser.add_argument("-o", "--output-dir", default="stereo_test",
	                    help="Output directory. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	"""
	image = Image.open(args.input_left)
	print "image.size", image.size
	data_list = list(image.getdata())
	print "data_list", data_list
	data_array = numpy.array(data_list, dtype=numpy.uint8)
	print "data_array", data_array
	data_array_reshaped = numpy.reshape(data_array, tuple(list(image.size)[::-1]+[3]))
	print "data_array_reshaped", data_array_reshaped
	image2 = Image.fromarray(data_array_reshaped, mode=image.mode)
	#image2 = Image.frombytes(mode=image.mode, size=image.size, data=data_array_reshaped)
	print "image2.size", image2.size
	data_list = list(image2.getdata())
	print "data_list", data_list
	data_array = numpy.array(data_list, dtype=numpy.uint8)
	print "data_array", data_array
	data_array_reshaped = numpy.reshape(data_array, tuple(list(image2.size)[::-1]+[3]))
	print "data_array_reshaped", data_array_reshaped
	image2.save(args.output)
	"""
	
	# create output dir
	if not os.path.exists(args.output_dir):
		os.makedirs(args.output_dir)
		log.info("Created \"{output}\".".format(output=args.output_dir))
	
	# copy inputs
	left_extension = os.path.splitext(args.input_left)[-1]
	left_output_filename =  os.path.join(args.output_dir, "01_left"+left_extension)
	shutil.copy(args.input_left, left_output_filename)
	left_image = Image.open(left_output_filename)
	
	right_extension = os.path.splitext(args.input_right)[-1]
	right_output_filename = os.path.join(args.output_dir, "01_right"+right_extension)
	shutil.copy(args.input_right, right_output_filename)
	right_image = Image.open(right_output_filename)
	
	# convert inputs to grayscale
	gray_left_image = left_image.convert("L")
	gray_left_output_filename =  os.path.join(args.output_dir, "02_gray_left"+left_extension)
	save_image(gray_left_image, gray_left_output_filename)
	
	gray_right_image = right_image.convert("L")
	gray_right_output_filename =  os.path.join(args.output_dir, "02_gray_right"+right_extension)
	save_image(gray_right_image, gray_right_output_filename)
	
	# superpose images
	superposition_image = ImageChops.add(left_image, right_image, scale=2.0, offset=0)
	superposition_filename =  os.path.join(args.output_dir, "03_superposition"+left_extension)
	save_image(superposition_image, superposition_filename)
	
	gray_superposition_image = ImageChops.add(gray_left_image, gray_right_image, scale=2.0, offset=0)
	gray_superposition_filename =  os.path.join(args.output_dir, "03_gray_superposition"+left_extension)
	save_image(gray_superposition_image, gray_superposition_filename)
	
	# ratio images
	ratio_image = get_ratio_images(left_image, right_image)
	ratio_filename =  os.path.join(args.output_dir, "04_ratio"+left_extension)
	save_image(ratio_image, ratio_filename)
	
	gray_ratio_image = get_ratio_images(gray_left_image, gray_right_image)
	gray_ratio_filename =  os.path.join(args.output_dir, "04_gray_ratio"+left_extension)
	save_image(gray_ratio_image, gray_ratio_filename)


if __name__ == "__main__":
	main()

