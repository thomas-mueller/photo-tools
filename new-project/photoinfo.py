
# -*- coding: utf-8 -*-

import hashlib
import os
import subprocess
import sys


class MemoryCache(object):
	def __init__(self):
		self.cache = {}
	
	def load_cached(self, input_file, *exiftool_arguments):
		key = tuple([input_file]+list(exiftool_arguments))
		if key not in self.cache:
			self.cache[key] = self.function(input_file, *exiftool_arguments)
		return self.cache[key]
	
	def __call__(self, function):
		self.function = function
		return self.load_cached


class FileCache(object):
	
	def load_cached(self, input_file, *exiftool_arguments):
		cache_file = input_file+"."+hashlib.md5(str(exiftool_arguments)).hexdigest()
		cache_file = os.path.join(os.path.dirname(cache_file), "."+os.path.basename(cache_file))
		if os.path.exists(cache_file):
			with open(cache_file, "r") as cache:
				return cache.read()
		else:
			exif_info = self.function(input_file, *exiftool_arguments)
			with open(cache_file, "w") as cache:
				cache.write(exif_info)
			return exif_info
	
	def __call__(self, function):
		self.function = function
		return self.load_cached


@MemoryCache()
@FileCache()
def load_exif_field(input_file, *exiftool_arguments):
	return subprocess.check_output(["exiftool"]+list(exiftool_arguments)+["-s3", input_file]).replace("\n", "")


for index in xrange(10):
	for arg in sys.argv[1:]:
		print arg, load_exif_field(arg, "-d", "%Y:%m:%d %H:%M:%S", "-DateTimeOriginal")

