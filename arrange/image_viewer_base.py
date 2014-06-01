#! /usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore



###################################################################################################
class ImageViewerBase(QtGui.QGraphicsView):
	
	def __init__(self, inputFiles=[], windowTitleBase="Image Viewer"):
		super(ImageViewerBase, self).__init__()
		
		self.isLoading = False
		
		self.inputFiles = inputFiles
		self.indexInputFile = 0
		
		self.windowTitleBase = windowTitleBase
		
		self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
		
		self.graphicsScene = QtGui.QGraphicsScene()
		self.setScene(self.graphicsScene)
		
		self.graphicsPixmapItem = QtGui.QGraphicsPixmapItem()
		self.graphicsScene.addItem(self.graphicsPixmapItem)
		
		#self.loadNextInput()
		
		self.setGeometry(0, 0, 800, 800)
		self.setWindowTitle(self.windowTitleBase)
		self.show()
	
	def currentInputFile(self): return self.inputFiles[self.indexInputFile]
	
	def loadNextInput(self, index=None):
		self.isLoading = True
		
		if index != None: self.indexInputFile = index
		if self.indexInputFile < 0: self.indexInputFile = 0
		elif self.indexInputFile >= len(self.inputFiles):
			self.close()
			return
		
		self.graphicsPixmapItem.setPixmap(QtGui.QPixmap(self.currentInputFile()))
		#self.fitInView(QtCore.QRect(QtCore.QPoint(0, 0), self.graphicsPixmapItem.pixmap().size()), QtCore.Qt.KeepAspectRatio)
		self.fitInView(self.graphicsScene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
		self.centerOn(self.graphicsPixmapItem)
		
		self.setWindowTitle(self.windowTitleBase + ": " + self.inputFiles[self.indexInputFile] + " ("+str(self.indexInputFile+1)+"/"+str(len(self.inputFiles))+")")
		
		self.isLoading = False
		
		
	def keyPressEvent(self, event):
		# http://qt-project.org/doc/qt-4.8/qt.html#Key-enum
		if event.key() == QtCore.Qt.Key_Space:
			if not self.isLoading: self.loadNextInput(self.indexInputFile + 1)
		elif event.key() == QtCore.Qt.Key_Backspace:
			if not self.isLoading: self.loadNextInput(self.indexInputFile - 1)
		if event.key() == QtCore.Qt.Key_N:
			if not self.isLoading: self.loadNextInput(self.indexInputFile + 10)
		elif event.key() == QtCore.Qt.Key_P:
			if not self.isLoading: self.loadNextInput(self.indexInputFile - 10)
		elif event.key() == QtCore.Qt.Key_F11:
			if self.windowState() == QtCore.Qt.WindowFullScreen:
				self.setWindowState(QtCore.Qt.WindowNoState)
				self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
			else:
				self.setWindowState(QtCore.Qt.WindowFullScreen)
				self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black))
		elif event.key() == QtCore.Qt.Key_Escape:
			if self.windowState() == QtCore.Qt.WindowFullScreen:
				self.setWindowState(QtCore.Qt.WindowNoState)
				self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
		else: super(ImageViewerBase, self).keyPressEvent(event)
	
	def resizeEvent(self, event):
		super(ImageViewerBase, self).resizeEvent(event)
		
		#self.fitInView(QtCore.QRect(QtCore.QPoint(0, 0), self.graphicsPixmapItem.pixmap().size()), QtCore.Qt.KeepAspectRatio)
		self.fitInView(self.graphicsScene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
		self.centerOn(self.graphicsPixmapItem)

