
# -*- coding: utf-8 -*-

import glob
import os

import tools


def get_files(directory, extensions):
	files = tools.flatten([glob.glob(os.path.join(directory, "*.%s" % ext)) for ext in extensions])
	return list(set(files))
	
