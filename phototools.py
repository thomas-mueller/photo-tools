
# -*- coding: utf-8 -*-

import math
import os
import subprocess
import time

import filecache
import progressiterator


date_format = "%Y:%m:%d %H:%M:%S"


@filecache.MemoryCache()
@filecache.FileCache()
def load_exif_field(input_file, *exiftool_arguments):
	output = None
	try:
		output = subprocess.check_output(["exiftool"]+list(exiftool_arguments)+["-s3", input_file]).replace("\n", "")
	except:
		pass
	return output


@filecache.MemoryCache()
@filecache.FileCache()
def load_image_dimensions(input_file, *identify_arguments):
	output = None
	try:
		output = subprocess.check_output(["identify"]+list(identify_arguments)+["-format", "%[fx:w] %[fx:h]", input_file]).replace("\n", "")
	except:
		pass
	return output


def is_portrait_format(input_file):
	dimensions = load_image_dimensions(input_file)
	if not (dimensions is None):
		dimensions = [int(dim) for dim in dimensions.split()]
		return dimensions[0] < dimensions[1]
	else:
		return False


def convert_date(date, date_format=date_format):
	if isinstance(date, basestring):
		return time.mktime(time.strptime(date, date_format)) if date != "" else None
	else:
		return time.strftime(date_format, time.localtime(date))


class FileDate(object):
	def __init__(self, file, date):
		self.file = file
		self.date = int(convert_date(date) if isinstance(date, basestring) else date) if date else 0
	
	def __lt__(self, other):
		if self.date != other.date:
			return self.date < other.date
		else:
			return os.path.splitext(os.path.basename(self.file))[0] < os.path.splitext(os.path.basename(other.file))[0]
	
	def __eq__(self, other):
		return (self.date == other.date) and (os.path.splitext(os.path.basename(self.file))[0] == os.path.splitext(os.path.basename(other.file))[0])
	
	def __str__(self):
		return "FileDate(%s, %s)" % (self.file, convert_date(self.date))

	@staticmethod
	def get_files_dates(files, exif_date_tag):
		files_dates = []
		for file in progressiterator.ProgressIterator(files, description="Load EXIF date infos"):
			date = load_exif_field(file, *["-d", date_format, "-%s" % exif_date_tag])
			if not (date is None):
				files_dates.append(FileDate(file, date))
		return files_dates

	@staticmethod
	def rename_files(files_dates, new_name):
		if len(files_dates) == 0:
			return []
		
		prepared_files_dates = [[files_dates[0]]]
		for file_date in files_dates[1:]:
			if file_date == prepared_files_dates[-1][-1]:
				prepared_files_dates[-1].append(file_date)
			else:
				prepared_files_dates.append([file_date])
		
		name_format = new_name + "_%s_%0" + str(int(math.floor(math.log10(len(prepared_files_dates))))+1) + "d"
		rename_files = []
		for index, files_dates in enumerate(prepared_files_dates):
			for file_date in files_dates:
				new_file_name = name_format % (convert_date(file_date.date, "%F"), index+1)
				new_file_name = os.path.join(os.path.dirname(file_date.file), new_file_name+os.path.splitext(file_date.file)[-1])
				rename_files.append((file_date.file, new_file_name))
		return rename_files
