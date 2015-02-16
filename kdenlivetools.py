
# -*- coding: utf-8 -*-

import logging
import logger
log = logging.getLogger(__name__)

import xml.etree.ElementTree as ElementTree



class KdenliveProject(object):
	def __init__(self, project_file):
		self.project_file = project_file
		self.project = ElementTree.parse(self.project_file)
	
	def save(self, output_file):
		self.project.write(output_file)

