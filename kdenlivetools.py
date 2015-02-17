
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import xml.etree.ElementTree as ElementTree



class KdenliveProject(object):
	def __init__(self, project_file):
		self.project_file = project_file
		self.project = ElementTree.parse(self.project_file)
		self.project_root = self.project.getroot()
	
	def add_images(self, images):
		playlists = [playlist for playlist in self.project_root.iter("playlist") if "playlist" in playlist.attrib.get("id", "")]
		
		for index, image in enumerate(images):
			producer_attrib = {
				"id" : str(index),
				"in" : str(index*7*24),
				"out" : str(((index+1)*7*24) - 1),
			}
			producer = ElementTree.SubElement(self.project_root, "producer", producer_attrib)
			
			producer_property = ElementTree.SubElement(producer, "property", {"name":"resource"})
			producer_property.text = image
			
			playlist_entry_attrib = {
				"producer" : str(index),
				"in" : str(index*7*24),
				"out" : str(((index+1)*7*24) - 1),
			}
			playlist_entry = ElementTree.SubElement(playlists[-(index % 2)], "element", playlist_entry_attrib)
			
			playlist_blank_attrib = {
				"length" : str(7*24),
			}
			playlist_blank = ElementTree.SubElement(playlists[-((index+1) % 2)], "blank", playlist_blank_attrib)
	
	def save(self, output_file):
		self.project.write(output_file)

