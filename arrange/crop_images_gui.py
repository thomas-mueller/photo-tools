#! /usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import copy, glob, os, subprocess, sys, tempfile
from PySide import QtGui, QtCore

from image_viewer_base import ImageViewerBase



###################################################################################################
class ImageCropGui(ImageViewerBase):

	def getCroppedSize(self, srcSize, destRatio):
		srcRatio = srcSize.height() / srcSize.width()
		croppedSize = copy.deepcopy(srcSize)
		if srcRatio > destRatio: croppedSize.setWidth(croppedSize.height() / destRatio)
		else: croppedSize.setHeight(croppedSize.width() * destRatio)
		return croppedSize

	def getCroppedRect(self, origSize, croppedSize, refShiftX=0.5, refShiftY=0.5):
		croppedRect = QtCore.QRect(QtCore.QPoint(0, 0), croppedSize)
		croppedRect.translate((origSize.width() - croppedSize.width()) * refShiftX,
		                      (origSize.height() - croppedSize.height()) * refShiftY)
		return croppedRect
	
	def shiftParameter(self, parameter, direction=1, shift=None):
		if not shift: shift = self.options.shift
		parameter += (direction * shift)
		if parameter < 0.0: parameter = 0.0
		elif parameter > 1.0: parameter = 1.0
		return parameter
	
	def scaleRectToFitInSize(self, srcRect, destSize):
		scaledRect = copy.deepcopy(srcRect)
		scaledSize = scaledRect.size()
		scaledSize.scale(destSize, QtCore.Qt.KeepAspectRatio)
		scaledRect.setSize(scaledSize)
		scaleFactor = scaledRect.width() / srcRect.width()
		scaledRect.translate(scaledRect.topLeft() * (scaleFactor - 1.0))
		return scaledRect
	
	def __init__(self, options, args):
		self.options = options
		inputFiles = sum(map(lambda arg: glob.glob(os.path.join(arg, "*")) if os.path.isdir(arg) else [arg], args), [])
		inputFiles.sort()
		
		super(ImageCropGui, self).__init__(inputFiles, "Image Crop Tool")
		
		self.graphicsPolygonItem = QtGui.QGraphicsPolygonItem()
		self.graphicsPolygonItem.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, int(self.options.shade_alpha * 255))))
		self.graphicsPolygonItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
		self.graphicsScene.addItem(self.graphicsPolygonItem)
		
		startIndex = None
		if options.start.isdigit(): startIndex = (int(options.start) - 1)
		elif options.start in inputFiles: startIndex = inputFiles.index(options.start)
		self.loadNextInput(index=startIndex)
	
	def loadNextInput(self, index=None):
		super(ImageCropGui, self).loadNextInput(index)
		
		self.refShiftX = 0.5
		self.refShiftY = 0.5
		self.moveCroppedRect()
		
	
	def moveCroppedRect(self):
		croppedSize = self.getCroppedSize(self.graphicsPixmapItem.pixmap().size(), self.options.dim_y / self.options.dim_x)
		self.cropRect = self.getCroppedRect(self.graphicsPixmapItem.pixmap().size(), croppedSize, self.refShiftX, self.refShiftY)
		
		originalRect = QtCore.QRect(QtCore.QPoint(0, 0), self.graphicsPixmapItem.pixmap().size())
		croppedPolygon = QtGui.QPolygon([originalRect.topLeft(), originalRect.bottomLeft(), originalRect.bottomRight(), originalRect.topRight(),
		                                  originalRect.topLeft(), self.cropRect.topLeft(), self.cropRect.bottomLeft(), self.cropRect.bottomRight(),
		                                  self.cropRect.topRight(), self.cropRect.topLeft(), originalRect.topLeft()])
		self.graphicsPolygonItem.setPolygon(croppedPolygon)
	
	def saveCropedImage(self):
		if not os.path.exists(self.options.output_dir): os.makedirs(self.options.output_dir)
	
		finalCroppedRect = self.scaleRectToFitInSize(self.cropRect, self.graphicsPixmapItem.pixmap().size())
		convertCommand = "convert {IN} -crop {W}x{H}+{X}+{Y} {OUT}".format(
				IN=self.inputFiles[self.indexInputFile],
				W=finalCroppedRect.width(), H=finalCroppedRect.height(), X=finalCroppedRect.left(), Y=finalCroppedRect.top(),
				OUT=os.path.join(self.options.output_dir, os.path.basename(self.inputFiles[self.indexInputFile])))
		print convertCommand
		
		self.indexInputFile += 1
		self.loadNextInput()
		
		os.system(convertCommand)
		
	def keyPressEvent(self, event):
		# http://qt-project.org/doc/qt-4.8/qt.html#Key-enum
		if event.key() == QtCore.Qt.Key_Up:
			self.refShiftY = self.shiftParameter(self.refShiftY, -1.0)
			self.moveCroppedRect()
		elif event.key() == QtCore.Qt.Key_Down:
			self.refShiftY = self.shiftParameter(self.refShiftY, +1.0)
			self.moveCroppedRect()
		elif event.key() == QtCore.Qt.Key_Left:
			self.refShiftX = self.shiftParameter(self.refShiftX, -1.0)
			self.moveCroppedRect()
		elif event.key() == QtCore.Qt.Key_Right:
			self.refShiftX = self.shiftParameter(self.refShiftX, +1.0)
			self.moveCroppedRect()
		elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
			self.saveCropedImage()
		elif event.key() == QtCore.Qt.Key_Space:
			self.indexInputFile += 1
			self.loadNextInput()
		else: super(ImageCropGui, self).keyPressEvent(event)
		


###################################################################################################
def main():
	parser = OptionParser(usage="usage: %prog [options] <DIRECTORY1 | FILE1> ...",
						  description="Crop images to a certain aspect ratio (x/y). The cropping rectangle is moved interactively.")

	parser.add_option("-x", "--dim-x", default=16.0, type=float, help="X dimension. [Default: 16]")
	parser.add_option("-y", "--dim-y", default=9.0, type=float, help="Y dimension. [Default: 9]")
	parser.add_option("-o", "--output-dir", help="Output directory.")
	parser.add_option("-s", "--start", default="1", help="Start index or file name. [Default: 1]")
	
	parser.add_option("--shade-alpha", default=0.6, type=float, help="Alpha value [0, 1] for the shaded area. [Default: 0.6]")
	parser.add_option("--shift", default=0.02, type=float, help="Shift applied to the cropping rectangle in units of the image dimensions. [Default: 0.02]")
	
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
	
	application = QtGui.QApplication(sys.argv)
	imageCropGui = ImageCropGui(options, args)
	
	return application.exec_()

if __name__ == "__main__": main()

