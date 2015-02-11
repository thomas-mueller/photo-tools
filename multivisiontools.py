
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import glob
import os
import shlex
import tempfile

import phototools
import progressiterator
import tools


class Multivision(object):
	def __init__(self, frame_rate=25.0, resolution=(1920, 1080), video_format="mp4"):
		self.frame_rate = frame_rate
		self.resolution = resolution
		self.video_format = video_format
	
	
	def _check_output_video_file(self, video_file=None):
		checked_video_file = video_file
		if checked_video_file is None:
			checked_video_file = tempfile.mkstemp(prefix="phototools_", suffix="."+self.video_format)[1]
		if os.path.exists(checked_video_file):
			os.remove(checked_video_file)
		return checked_video_file
	
	
	def _prepare_image(self, image_file):
		image_file_info = os.path.splitext(os.path.basename(image_file))
		prepared_image_file = tempfile.mkstemp(prefix=image_file_info[0]+"_", suffix=image_file_info[1])[1]
		command = "convert %s -resize %dx%d^ -gravity center -extent %dx%d %s" % (
				image_file,
				self.resolution[0], self.resolution[1],
				self.resolution[0], self.resolution[1],
				prepared_image_file
		)
		logger.subprocessCall(shlex.split(command))
		return prepared_image_file
	
	
	def image_transition_to_video(self, image_file1, image_file2, transition_time=1.0, video_file=None):
		# determine video file
		video_file = self._check_output_video_file(video_file)
		
		# crop/resize source images
		prepared_image_file1 = self._prepare_image(image_file1)
		prepared_image_file2 = self._prepare_image(image_file2)
		temporary_files = [prepared_image_file1, prepared_image_file2]
		
		# morph transtion frames
		prepared_image_file_info = os.path.splitext(prepared_image_file1)
		morphed_files = "%s_morphed%s%s" % (prepared_image_file_info[0], "%05d", prepared_image_file_info[1])
		n_frames = int(transition_time * self.frame_rate)
		command = "convert %s %s -morph %d %s" % (
				prepared_image_file1, prepared_image_file2,
				n_frames-2, morphed_files
		)
		logger.subprocessCall(shlex.split(command))
		temporary_files.extend(glob.glob(morphed_files.replace("%05d", "*")))
		
		# encode video
		command = "ffmpeg -loglevel quiet -r %f -i %s %s" % (self.frame_rate, morphed_files, video_file)
		logger.subprocessCall(shlex.split(command))
		
		# remove temporary files
		for temporary_file in temporary_files:
			os.remove(temporary_file)
		
		# return video file
		return video_file
	
	
	def image_to_video(self, image_file, duration=1.0, video_file=None):
		return self.image_transition_to_video(image_file, image_file, transition_time=duration, video_file=video_file)
	
	
	def concatenate_videos(self, video_files, concatenated_video_file=None):
		# determine video file
		concatenated_video_file = self._check_output_video_file(concatenated_video_file)
		
		# create list of vidoes to concatenate
		videos_list_file = tempfile.mkstemp(prefix="phototools_", suffix=".txt")[1]
		temporary_files = [videos_list_file]
		with open(videos_list_file, "w") as videos_list:
			videos_list.write("\n".join(["file '%s'" % v for v in video_files]))
		
		# concatenate videos
		command = "ffmpeg -loglevel quiet -f concat -i %s -c copy %s" % (videos_list_file, concatenated_video_file)
		logger.subprocessCall(shlex.split(command))
		
		# remove temporary files
		for temporary_file in temporary_files:
			os.remove(temporary_file)
		
		# return video file
		return concatenated_video_file
	
	
	def images_to_video(self, image_files, image_durations=[5.0], transition_times=[1.0], video_file=None):
		# determine video file
		video_file = self._check_output_video_file(video_file)
		
		# check parameter list lengths
		if len(image_durations) > 1 and len(image_durations) < len(image_files):
			log.warning("Not enough image durations specified.")
		image_durations = (image_durations*len(image_files))[:len(image_files)]
		
		if len(transition_times) > 1 and len(transition_times) < (len(image_files) - 1):
			log.warning("Not enough image transition times specified.")
		transition_times = (transition_times*(len(image_files)-1))[:(len(image_files)-1)]
		
		# create image videos
		image_videos = [
				self.image_to_video(image_file, duration)
				for image_file, duration
				in progressiterator.ProgressIterator(zip(image_files, image_durations), description="Process images")
		]
		
		# create transition videos
		transition_videos = [
				self.image_transition_to_video(image_file1, image_file2, transition_time)
				for image_file1, image_file2, transition_time
				in progressiterator.ProgressIterator(zip(image_files[:-1], image_files[1:], transition_times), description="Process image transitions")
		]
		
		# concatenate videos
		video_files = tools.flatten(zip(image_videos[:-1], transition_videos))+[image_videos[-1]]
		temporary_files = video_files
		self.concatenate_videos(video_files, concatenated_video_file=video_file)
		
		# remove temporary files
		for temporary_file in temporary_files:
			os.remove(temporary_file)
		
		# return video file
		return video_file

