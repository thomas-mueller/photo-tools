#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import numpy
import os
from PIL import Image, ImageChops
import ROOT
import shutil



def save_image(image, filename):
	image.save(filename)
	log.info("Saved image \"{image}\".".format(image=filename))


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
	return ratio_image, ratio_image.point(lambda x: 255-x)


def get_fft_image(image):
	gray_image = image.convert("L")
	image_data = numpy.array(gray_image.getdata(), dtype=numpy.uint8).reshape(gray_image.size[::-1])
	fft = numpy.fft.fft2(image_data)
	fft[0, 0] = 0
	abs_shifted_fft = numpy.abs(numpy.fft.fftshift(fft))
	return Image.fromarray(numpy.array(abs_shifted_fft * (255.0 / numpy.amax(abs_shifted_fft)), dtype=numpy.uint8), mode=gray_image.mode)


def get_fft_histogram(image, root_directory, name):
	gray_image = image.convert("L")
	image_data = numpy.array(gray_image.getdata(), dtype=numpy.uint8).reshape(gray_image.size[::-1])
	shifted_fft = numpy.fft.fftshift(numpy.fft.fft2(image_data))
	
	def _to_histogram(array, name):
		histogram = ROOT.TH2F(name, "", gray_image.size[0]-1, 0.0, gray_image.size[0]-1, gray_image.size[1]-1, 0.0, gray_image.size[1]-1)
		for x_index in xrange(gray_image.size[0]-1):
			for y_index in xrange(gray_image.size[1]-1):
				histogram.SetBinContent(x_index+1, y_index+1, array[y_index, x_index])
		return histogram
	
	root_directory.cd()
	histograms = [_to_histogram(array, name+"_"+prefix) for array, prefix in [[numpy.abs(shifted_fft), "abs"], [numpy.angle(shifted_fft), "arg"], [numpy.real(shifted_fft), "re"], [numpy.imag(shifted_fft), "im"]]]
	for histogram in histograms:
		histogram.Write()
	return histograms


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
	
	root_output_filename = os.path.join(args.output_dir, "output.root")
	root_output_file = ROOT.TFile(root_output_filename, "RECREATE")
	
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
	
	# FFT of superpositions
	get_fft_histogram(gray_superposition_image, root_output_file, "superposition_fft")
	gray_superposition_fft_image = get_fft_image(gray_superposition_image)
	gray_superposition_fft_filename =  os.path.join(args.output_dir, "03_gray_superposition_fft"+left_extension)
	save_image(gray_superposition_fft_image, gray_superposition_fft_filename)
	
	# ratio images
	left_ratio_image, right_ratio_image = get_ratio_images(left_image, right_image)
	left_ratio_filename =  os.path.join(args.output_dir, "04_left_ratio"+left_extension)
	save_image(left_ratio_image, left_ratio_filename)
	right_ratio_filename =  os.path.join(args.output_dir, "04_right_ratio"+right_extension)
	save_image(right_ratio_image, right_ratio_filename)
	
	# grayscale ratio images
	gray_left_ratio_image, gray_right_ratio_image = get_ratio_images(gray_left_image, gray_right_image)
	gray_left_ratio_filename =  os.path.join(args.output_dir, "05_gray_left_ratio"+left_extension)
	save_image(gray_left_ratio_image, gray_left_ratio_filename)
	
	gray_right_ratio_filename =  os.path.join(args.output_dir, "05_gray_right_ratio"+right_extension)
	save_image(gray_right_ratio_image, gray_right_ratio_filename)
	
	# FFT of superpositions
	get_fft_histogram(gray_left_ratio_image, root_output_file, "left_ratio_fft")
	gray_left_ratio_fft_image = get_fft_image(gray_left_ratio_image)
	gray_left_ratio_fft_filename =  os.path.join(args.output_dir, "05_gray_left_ratio_fft"+left_extension)
	save_image(gray_left_ratio_fft_image, gray_left_ratio_fft_filename)
	
	get_fft_histogram(gray_right_ratio_image, root_output_file, "right_ratio_fft")
	gray_right_ratio_fft_image = get_fft_image(gray_right_ratio_image)
	gray_right_ratio_fft_filename =  os.path.join(args.output_dir, "05_gray_right_ratio_fft"+right_extension)
	save_image(gray_right_ratio_fft_image, gray_right_ratio_fft_filename)
	
	#root_output_file.Write()
	root_output_file.Close()
	log.info("Saved ROOT output \"{output}\".".format(output=root_output_filename))

if __name__ == "__main__":
	main()

