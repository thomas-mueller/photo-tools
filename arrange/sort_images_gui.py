#! /usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import copy, glob, math, os, subprocess, sys, tempfile
from PySide import QtGui, QtCore

from image_viewer_base import ImageViewerBase



###################################################################################################
class ImageSortGui(ImageViewerBase):
	
	def __init__(self, options, args):
		self.options = options
		inputFiles = sum(map(lambda arg: glob.glob(os.path.join(arg, "*")) if os.path.isdir(arg) else [arg], args), [])
		inputFiles.sort()
		
		super(ImageSortGui, self).__init__(inputFiles, "Image Sort Tool")
		
		self.sortedFiles = []
		self.indexLastSorted = None
		self.indexOccurence = 0
		self.indexSortedMarked = None
		self.indexOccurenceMarked = None
		self.savedSortedFiles = []
		
		self.graphicsTextItem = QtGui.QGraphicsTextItem()
		font = self.graphicsTextItem.font()
		font.setPixelSize(0.1 * self.height())
		self.graphicsTextItem.setFont(font)
		self.graphicsScene.addItem(self.graphicsTextItem)
		
		self.importSortResults()
		self.loadNextInput()

	def indices(self, searchList, searchItem): return [index for index, item in enumerate(searchList) if item==searchItem]
	
	def sortedPositions(self, sortedFiles=None, inputFile=None): return self.indices(self.sortedFiles, self.currentInputFile())
	
	def setLabel(self):
		numberOfImages = len(self.sortedFiles)
		
		def positionLabel(index, position):
			label = str(position + 1)
			if self.indexSortedMarked != None and self.indexOccurenceMarked != None and self.currentInputFile() == self.sortedFiles[self.indexSortedMarked] and index == self.indexOccurenceMarked:
				label = "<font color=\"#FF0000\">" + label + "</font>"
			if index == self.indexOccurence: label = "<b>" + label + "</b>"
			return label
		
		label = ""
		if len(self.sortedPositions()) > 0:
			label += "<body bgcolor=\"#FFFFFF\">&nbsp;"
			label += reduce(lambda a, b: a+", "+b, [positionLabel(index, position) for index, position in enumerate(self.sortedPositions())])
			label += " of " + str(numberOfImages) + "&nbsp;</body>"
			
			self.indexLastSorted = self.sortedPositions()[self.indexOccurence]
		
		self.graphicsTextItem.setHtml(label)
	
	def loadNextInput(self, index=None):
		super(ImageSortGui, self).loadNextInput(index)
		self.indexOccurence = len(self.sortedPositions()) - 1
		self.setLabel()
	
	def loadNextSortedInput(self, direction=1):
		if self.indexLastSorted != None or len(self.sortedFiles) > 0:
			newSortedIndex = (self.indexLastSorted + (1 if direction > 0 else -1)) if self.indexLastSorted != None else 0
			if newSortedIndex < 0: newSortedIndex = 0
			elif newSortedIndex >= len(self.sortedFiles): newSortedIndex = len(self.sortedFiles) - 1
			self.loadNextInput(self.inputFiles.index(self.sortedFiles[newSortedIndex]))
			# TODO set self.indexOccurence
	
	def insertFile(self, append=True):
		insertIndex = len(self.sortedFiles) if append else 0
		if self.indexSortedMarked != None and self.indexOccurenceMarked != None:
			insertIndex = self.indexSortedMarked + (1 if append else 0)
		self.sortedFiles.insert(insertIndex, self.currentInputFile())
		self.indexOccurence = self.sortedPositions().index(insertIndex)
		#if self.indexSortedMarked != None and self.indexOccurenceMarked != None:
		#	self.indexSortedMarked = self.sortedPositions()[self.indexOccurence]
		#	self.indexOccurenceMarked = self.indexOccurence
		self.indexSortedMarked = None
		self.indexOccurenceMarked = None
		self.setLabel()
	
	def deleteFile(self):
		self.sortedFiles.pop(self.sortedPositions()[self.indexOccurence])
		self.indexOccurence -= 1
		if self.indexOccurence < 0 and len(self.sortedPositions()) > 0: self.indexOccurence = 0
		self.setLabel()
	
	def shiftIndexOccurence(self, direction=1):
		if direction > 0: self.indexOccurence += 1
		else: self.indexOccurence -= 1
		if self.indexOccurence < 0: self.indexOccurence = 0
		else:
			maxIndexOccurence = len(self.sortedPositions()) - 1
			if self.indexOccurence > maxIndexOccurence: self.indexOccurence = maxIndexOccurence
		self.setLabel()
	
	def shiftSortedIndex(self, direction=1):
		currentSortedIndex = self.sortedPositions()[self.indexOccurence]
		newSortedIndex = currentSortedIndex + (1 if direction > 0 else -1)
		if newSortedIndex >= 0 and newSortedIndex < len(self.sortedFiles):
			self.sortedFiles[newSortedIndex], self.sortedFiles[currentSortedIndex] = self.sortedFiles[currentSortedIndex], self.sortedFiles[newSortedIndex]
		if (self.sortedPositions()[self.indexOccurence] + (1 if direction > 0 else -1)) in self.sortedPositions(): self.shiftIndexOccurence(direction)
		else: self.setLabel()
		
	def toggleMarked(self):
		if len(self.sortedPositions()) > 0:
			if self.indexSortedMarked == self.sortedPositions()[self.indexOccurence] and self.indexOccurenceMarked == self.indexOccurence:
				self.indexSortedMarked = None
				self.indexOccurenceMarked = None
			else:
				self.indexSortedMarked = self.sortedPositions()[self.indexOccurence]
				self.indexOccurenceMarked = self.indexOccurence
			self.setLabel()
	
	def saveSortResults(self):
		for savedSortedFile in self.savedSortedFiles: os.unlink(savedSortedFile)
		self.savedSortedFiles = []
	
		if len(self.sortedFiles) > 0:
			if not os.path.exists(self.options.output_dir): os.makedirs(self.options.output_dir)
			nDigits = int(math.floor(math.log10(len(self.sortedFiles)))) + 1
		
			for index, sortedFile in enumerate(self.sortedFiles):
				relSortedFile = os.path.relpath(os.path.abspath(sortedFile), os.path.abspath(self.options.output_dir))
				symlinkTarget = os.path.join(self.options.output_dir, self.options.prefix+(str(index+1).rjust(nDigits, "0"))+"."+sortedFile.split(".")[-1])
				print sortedFile, "-->", symlinkTarget				
				if os.path.exists(symlinkTarget): os.unlink(symlinkTarget)
				os.symlink(relSortedFile, symlinkTarget)
				self.savedSortedFiles.append(os.path.join(self.options.output_dir, symlinkTarget))
	
	def importSortResults(self):
		if os.path.exists(self.options.output_dir):
			existingSymlinks = map(lambda entry: os.path.join(self.options.output_dir, entry), os.listdir(self.options.output_dir))
			existingSymlinks = filter(lambda entry: os.path.islink(entry), existingSymlinks)
			existingSymlinks.sort()
		
			expandedExistingSortedFiles = map(lambda entry: os.path.realpath(os.path.abspath(entry)), existingSymlinks)
			expandedInputFiles = map(lambda entry: os.path.realpath(os.path.abspath(entry)), self.inputFiles)
		
			for expandedExistingSortedFile in expandedExistingSortedFiles:
				if expandedExistingSortedFile in expandedInputFiles:
					self.sortedFiles.append(self.inputFiles[expandedInputFiles.index(expandedExistingSortedFile)])
				else: self.sortedFiles.append(expandedExistingSortedFile)
		
			self.savedSortedFiles = copy.deepcopy(existingSymlinks)
		
	def keyPressEvent(self, event):
		# http://qt-project.org/doc/qt-4.8/qt.html#Key-enum
		if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return: self.insertFile(True)
		elif event.key() == QtCore.Qt.Key_0: self.insertFile(False)
		elif event.key() == QtCore.Qt.Key_Delete: self.deleteFile()
		elif event.key() == QtCore.Qt.Key_Left: self.shiftIndexOccurence(-1)
		elif event.key() == QtCore.Qt.Key_Right: self.shiftIndexOccurence(1)
		elif event.key() == QtCore.Qt.Key_Minus: self.shiftSortedIndex(-1)
		elif event.key() == QtCore.Qt.Key_Plus: self.shiftSortedIndex(1)
		elif event.key() == QtCore.Qt.Key_M: self.toggleMarked()
		elif event.key() == QtCore.Qt.Key_P: self.loadNextSortedInput(-1)
		elif event.key() == QtCore.Qt.Key_N: self.loadNextSortedInput(1)
		elif event.key() == QtCore.Qt.Key_S: self.saveSortResults()
		elif event.key() == QtCore.Qt.Key_Q: super(ImageSortGui, self).close()
		elif event.key() == QtCore.Qt.Key_H or event.key() == QtCore.Qt.Key_Question:
			print ""
			print "Press Enter/Return to insert current image at the end of the sequence."
			print "Press Zero to insert current image at the beginning of the sequence."
			print "Press Delete to delete current image from the sequence."
			print "Press Left/Right to shift current occurence in case this image was added multiple times to the sequence."
			print "Press Plus/Minus to shift position of the current image in the sequence."
			print "Press M to toggle the marked state of the current occurence. In case an image is marked, insertions/deletions are made before/after this occurence"
			print "Press S to save current sequence to the output directory."
			print "Press Q to quit without saving."
			print ""
		else: super(ImageSortGui, self).keyPressEvent(event)
		
	def closeEvent(self, event):
		self.saveSortResults()
		super(ImageSortGui, self).closeEvent(event)
		


###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options] <DIRECTORY1 | FILE1> ...",
						  description="Sort images and create alphabetical symlinks. Press H to get a list of all shortcuts.")

	parser.add_option("-o", "--output-dir", help="Output directory.")
	parser.add_option("--prefix", default="a_", help="Prefix for sorted files. [Default: a_]")

	(options, args) = parser.parse_args()
	
	if len(args) < 1:
		print "ERROR: no inputs specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if not options.output_dir:
		print "ERROR: no output directory specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if os.path.exists(options.output_dir) and not os.path.isdir(options.output_dir):
		print "ERROR:", options.output_dir, "is not a directory!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	application = QtGui.QApplication(sys.argv)
	imageSortGui = ImageSortGui(options, args)
	
	return application.exec_()

if __name__ == "__main__": main()

