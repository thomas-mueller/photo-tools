
# -*- coding: utf-8 -*-

import hashlib
import os


class MemoryCache(object):
	def __init__(self):
		self.cache = {}
	
	def load_cached(self, input_file, *args):
		key = tuple([input_file]+list(args))
		if key not in self.cache:
			self.cache[key] = self.function(input_file, *args)
		return self.cache[key]
	
	def __call__(self, function):
		self.function = function
		return self.load_cached


class FileCache(object):
	
	def load_cached(self, input_file, *args):
		cache_file = input_file+"."+hashlib.md5(str(args)).hexdigest()
		cache_file = os.path.join(os.path.dirname(cache_file), "."+os.path.basename(cache_file))
		if os.path.exists(cache_file):
			with open(cache_file, "r") as cache:
				return cache.read()
		else:
			exif_info = self.function(input_file, *args)
			with open(cache_file, "w") as cache:
				cache.write(exif_info)
			return exif_info
	
	def __call__(self, function):
		self.function = function
		return self.load_cached

