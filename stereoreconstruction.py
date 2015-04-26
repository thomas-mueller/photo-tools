#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import math
import numpy
import ROOT



class RealObject(object):
	def __init__(self, position, depth, value):
		self.position = position
		self.depth = depth
		self.value = value
	
	def __str__(self):
		return "RealObject (position = {position:8.2f}, depth = {depth:8.2f}, value = {value:8.2f})".format(
				position=self.position, depth=self.depth, value=self.value
		)

class PhotoObject(object):
	def __init__(self, position, value):
		self.position = position # TODO: change to pixel index
		self.value = value
	
	def __str__(self):
		return "PhotoObject (position = {position:8.2f}, value = {value:8.2f})".format(
				position=self.position, value=self.value
		)

class Reality(object):
	def __init__(self, real_objects):
		self.real_objects = real_objects
		self.real_objects.sort(key=lambda real_object: real_object.depth)
	
	def __str__(self):
		return "Reality ({n} objects):\n\t{objects}".format(
				n=len(self.real_objects), objects="\n\t".join([str(real_object) for real_object in self.real_objects])
		)

class Photo(object):
	def __init__(self, camera, reality):
		self.photo_objects = camera.to_photo_objects(reality)
		self.photo_objects.sort(key=lambda photo_object: photo_object.position)
	
	def __str__(self):
		return "Photo ({n} objects):\n\t{objects}".format(
				n=len(self.photo_objects), objects="\n\t".join([str(photo_object) for photo_object in self.photo_objects])
		)

class Camera(object):
	def __init__(self, center, size, n_pixels, angle):
		self.center = center
		self.size = size
		self.n_pixels = n_pixels
		self.angle = angle
		
		self.depth = self.size / (2.0 * math.tan(math.radians(self.angle / 2.0)))
		self.pixel_size = self.size / self.n_pixels
	
	def __str__(self):
		return "Camera (center = {center}, size = {size}, n_pixels = {n_pixels}, angle = {angle})".format(
				center=self.center, size=self.size, n_pixels=self.n_pixels, angle=self.angle
		)
	
	def is_captured(self, photo_object):
		return abs(photo_object.position - self.center) < (self.size / 2.0)
	
	def to_pixel_index(self, photo_object):
		if not self.is_captured(photo_object):
			return None
		else:
			return int(math.floor((photo_object.position - self.center) / self.pixel_size))
	
	def to_real_object(self, photo_object, depth):
		position = ((photo_object.position - self.center) * depth / self.depth) + self.center
		return RealObject(position, depth, photo_object.value)
	
	def to_photo_object(self, real_object):
		position = ((real_object.position - self.center) * self.depth / real_object.depth) + self.center
		return PhotoObject(position, real_object.value)
	
	def to_photo_objects(self, reality):
		real_objects = [real_object for real_object in reality.real_objects if real_object.depth > self.depth]
		photo_objects = [self.to_photo_object(real_object) for real_object in real_objects]
		
		exposed_pixels = [False]*self.n_pixels
		photo_objects_indices_to_remove = []
		for index, (real_object, photo_object) in enumerate(zip(real_objects, photo_objects)):
			pixel_index = self.to_pixel_index(photo_object)
			if pixel_index is None:
				photo_objects_indices_to_remove.append(index)
			else:
				if exposed_pixels[pixel_index]:
					photo_objects_indices_to_remove.append(index)
				else:
					exposed_pixels[pixel_index] = True
		
		for index in photo_objects_indices_to_remove[::-1]:
			photo_objects.pop(index)
		
		return photo_objects
	
	def to_histogram(self, photo, root_directory=ROOT.gDirectory, name="photo"):
		root_directory.cd()
		histogram = ROOT.TH1F(name, "", n_pixels, center + (size / (-2.0)), center + (size /2.0))
		for photo_object in photo.photo_objects:
			histogram.SetBinContent(histogram.FindBin(photo_object.position), photo_object.value)
		return histogram


def main():
	parser = argparse.ArgumentParser(description="Stereo Reconstrucion.", parents=[logger.loggingParser])
	
	parser.add_argument("--camera-1-center", type=float, default=-10.0,
	                    help="Camera 1 center. [Default: %(default)s]")
	parser.add_argument("--camera-1-size", type=float, default=10.0,
	                    help="Camera 1 size. [Default: %(default)s]")
	parser.add_argument("--camera-1-n-pixels", type=int, default=20,
	                    help="Camera 1 number of pixels. [Default: %(default)s]")
	parser.add_argument("--camera-1-angle", type=float, default=45.0,
	                    help="Camera 1 center. [Default: %(default)s]")
	
	parser.add_argument("--camera-2-center", type=float, default=10.0,
	                    help="Camera 2 center. [Default: %(default)s]")
	parser.add_argument("--camera-2-size", type=float, default=10.0,
	                    help="Camera 2 size. [Default: %(default)s]")
	parser.add_argument("--camera-2-n-pixels", type=int, default=20,
	                    help="Camera 2 number of pixels. [Default: %(default)s]")
	parser.add_argument("--camera-2-angle", type=float, default=45.0,
	                    help="Camera 2 center. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	camera1 = Camera(args.camera_1_center, args.camera_1_size, args.camera_1_n_pixels, args.camera_1_angle)
	camera2 = Camera(args.camera_2_center, args.camera_2_size, args.camera_2_n_pixels, args.camera_2_angle)
	
	"""
	real_object = RealObject(0.0, 100.0, 1.0)
	#real_object = RealObject(5.0, 100.0, 1.0)
	#real_object = RealObject(10.0, 100.0, 1.0)
	print real_object
	photo_object1 = camera1.to_photo_object(real_object)
	print photo_object1
	real_object1 = camera1.to_real_object(photo_object1, 100.0)
	print real_object1
	photo_object2 = camera2.to_photo_object(real_object)
	print photo_object2
	real_object2 = camera2.to_real_object(photo_object2, 100.0)
	print real_object2
	"""
	
	reality = Reality([RealObject(index*10.0, 100, index) for index in xrange(-5, 6, 1)]+[RealObject(index*10.0, 200, index+100) for index in xrange(-5, 6, 1)])
	photo1 = Photo(camera1, reality)
	photo2 = Photo(camera2, reality)
	
	print reality
	print ""
	print camera1
	print photo1
	print ""
	print camera2
	print photo2
	

if __name__ == "__main__":
	main()

