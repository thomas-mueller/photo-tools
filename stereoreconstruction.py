#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import argparse
import math



class RealObject(object):
	def __init__(self, position, depth, value):
		self.position = position
		self.depth = depth
		self.value = value
	
	def __str__(self):
		return "RealObject(position={position}, depth={depth}, value={value}".format(
				position=self.position, depth=self.depth, value=self.value
		)

class PhotoObject(object):
	def __init__(self, position, value):
		self.position = position # TODO: change to pixel index
		self.value = value
	
	def __str__(self):
		return "PhotoObject(position={position}, value={value}".format(
				position=self.position, value=self.value
		)

class Reality(object):
	def __init__(self, real_objects):
		self.real_objects = real_objects
		self.real_objects.sort(key=lambda real_object: real_object.depth)
	
	def __str__(self):
		return "Reality({n} objects):\n\t{objects}".format(
				n=len(self.real_objects), objects="\n\t".join([str(real_object) for real_object in self.real_objects])
		)

class Photo(object):
	def __init__(self, camera, reality):
		self.photo_objects = camera.to_photo_objects(reality)
		self.photo_objects.sort(key=lambda photo_object: photo_object.position)
	
	def __str__(self):
		return "Photo({n} objects):\n\t{objects}".format(
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
	
	def is_captured(self, photo_object):
		return abs(photo_object.position - self.center) < (self.size / 2.0)
	
	def to_pixel_index(self, photo_object):
		if not self.is_captured(photo_object):
			return None
		else:
			return int(math.floor((photo_object.position - self.center) / self.pixel_size))
	
	def to_real_object(self, photo_object, depth):
		position = (photo_object.position * depth / self.depth) - self.center
		return RealObject(position, depth, photo_object.value)
	
	def to_photo_object(self, real_object):
		position = (real_object.position * self.depth / real_object.depth) + self.center
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


def main():
	parser = argparse.ArgumentParser(description="Stereo Reconstrucion.", parents=[logger.loggingParser])
	
	parser.add_argument("--camera-1-center", type=float, default=0.0,
	                    help="Camera 1 center. [Default: %(default)s]")
	parser.add_argument("--camera-1-size", type=float, default=10.0,
	                    help="Camera 1 size. [Default: %(default)s]")
	parser.add_argument("--camera-1-n-pixels", type=int, default=20,
	                    help="Camera 1 number of pixels. [Default: %(default)s]")
	parser.add_argument("--camera-1-angle", type=float, default=45.0,
	                    help="Camera 1 center. [Default: %(default)s]")
	
	args = parser.parse_args()
	logger.initLogger(args)
	
	camera = Camera(args.camera_1_center, args.camera_1_size, args.camera_1_n_pixels, args.camera_1_angle)
	
	reality = Reality([RealObject(index*10.0, 100, index) for index in xrange(-5, 6, 1)]+[RealObject(index*10.0, 200, index*100) for index in xrange(-5, 6, 1)])
	photo = Photo(camera, reality)
	
	print reality
	print ""
	print photo
	
	

if __name__ == "__main__":
	main()

