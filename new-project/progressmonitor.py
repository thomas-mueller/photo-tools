
# -*- coding: utf-8 -*-

import sys


class ProgressMonitor(object):
	def __init__(self, n_iterations, n_outputs=100):
		self.n_iterations = n_iterations
		self.n_outputs = n_outputs
		self.current_iteration = 0
		self.current_progress = -1
	
	def next(self, current_iteration = -1):
		if current_iteration > 0:
			self.current_iteration = current_iteration
		else:
			self.current_iteration += 1
		
		current_progress = int(self.n_outputs * self.current_iteration / self.n_iterations)
		if current_progress > self.current_progress:
			self.current_progress = current_progress
			sys.stdout.write("\r[" + (self.current_progress * "=") + ((self.n_outputs - self.current_progress) * ".") + "]")
			sys.stdout.flush()

