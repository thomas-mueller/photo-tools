
# -*- coding: utf-8 -*-

import abc
import hashlib
import os
import shutil
import tempfile


class Cache(object):
	def __call__(self, function_to_cache):
		self._function_to_cache = function_to_cache
		return self._get_cached
	
	@abc.abstractmethod
	def _get_cached(self, *args, **kwargs):
		pass


class MemoryCache(Cache):
	def __init__(self):
		self.cache = {}
	
	def _get_cached(self, *args, **kwargs):
		if args not in self.cache:
			self.cache[args] = self._function_to_cache(*args, **kwargs)
		return self.cache[args]


class FileCache(Cache):
	def _determine_cache_file(self, *args, **kwargs):
		args_hash = hashlib.md5("".join([str(a) for a in args])).hexdigest()
		
		for arg in list(args) + kwargs.keys():
			if isinstance(arg, basestring) and os.path.exists(arg):
				directory = os.path.dirname(arg)
				filename, extension = os.path.splitext(os.path.basename(arg))
				extension = kwargs.get("output_file_extension", extension)
				cache_dir = os.path.join(directory, "cache")
				if not os.path.exists(cache_dir):
					os.makedirs(cache_dir)
				return os.path.join(cache_dir, filename + "." + args_hash + extension)
		
		# no input file found, create cache file in temp dir
		cache_dir = os.path.join(tempfile.gettempdir(), "cache")
		if not os.path.exists(cache_dir):
			os.makedirs(cache_dir)
		return os.path.join(cache_dir, args_hash)
	
	def _get_cached(self, *args, **kwargs):
		cache_file = self._determine_cache_file(*args, **kwargs)
		if os.path.exists(cache_file):
			with open(cache_file, "r") as cache:
				return cache.read()
		else:
			result = self._function_to_cache(*args, **kwargs)
			with open(cache_file, "w") as cache:
				cache.write(result)
			return result


class FileProducerCache(FileCache):

	def _get_cached(self, *args, **kwargs):
		cache_file = self._determine_cache_file(*args, **kwargs)
		if not os.path.exists(cache_file):
			produced_file = self._function_to_cache(*args, **kwargs)
			if os.path.exists(produced_file):
				shutil.move(produced_file, cache_file)
			else:
				return produced_file
		return cache_file

