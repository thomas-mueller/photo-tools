#! /usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import math, sys, time, ROOT
# import xml.etree.ElementTree # http://docs.python.org/2/library/xml.etree.elementtree.html
from lxml import etree # http://lxml.de/tutorial.html


trkptKeys = ["lat", "lon", "ele", "time"]
earthRadius = 6371000.0
rootNtuple = None


def trkptToDict(trkpt, getNsPlusKey):
	global trkptKeys
	trkptDict = {}
	for key in trkptKeys[:2]: trkptDict[key] = float(trkpt.attrib[key])
	trkptDict[trkptKeys[2]] = float(trkpt.find(getNsPlusKey(trkptKeys[2])).text)
	trkptDict[trkptKeys[3]] = time.mktime(time.strptime(trkpt.find(getNsPlusKey(trkptKeys[3])).text, "%Y-%m-%dT%H:%M:%S"))
	return trkptDict


def geoToCartesion(listLatLonEle):
	theta = math.radians(listLatLonEle[0])
	phi = math.radians(listLatLonEle[1])
	radius = earthRadius + listLatLonEle[2]
	return [radius * math.cos(theta) * math.cos(phi),
	        radius * math.cos(theta) * math.sin(phi),
	        radius * math.sin(theta)]


def vector(srcTrkptDict, dstTrkptDict):
	global trkptKeys
	srcVector = geoToCartesion([srcTrkptDict[key] for key in trkptKeys[:3]])
	dstVector = geoToCartesion([dstTrkptDict[key] for key in trkptKeys[:3]])
	
	return [(b-a) for a, b in zip(srcVector, dstVector)]


def dotproduct(v1, v2): return sum((a*b) for a, b in zip(v1, v2))
def length(v): return math.sqrt(dotproduct(v, v))
def angle(vector1, vector2): return math.degrees(math.acos(dotproduct(vector1, vector2) / (length(vector1) * length(vector2))))


def determineRemoveMiddleTrkpt(trkpt2, trkpt3, trkpt4, getNsPlusKey, thresholdDistance, thresholdTime, thresholdAngle):
	global rootNtuple
	
	if trkpt2==None or trkpt3==None: return False
	
	trkptDict2 = trkptToDict(trkpt2, getNsPlusKey)
	trkptDict3 = trkptToDict(trkpt3, getNsPlusKey)
	trkptDict4 = trkptToDict(trkpt4, getNsPlusKey)
	
	vector34 = vector(trkptDict3, trkptDict4)
	vector23 = vector(trkptDict2, trkptDict3)
	
	distance = length(vector34)
	timeDifference = trkptDict4["time"]-trkptDict3["time"]
	angularDifference = angle(vector23, vector34)
	
	if rootNtuple: rootNtuple.Fill(distance, timeDifference, angularDifference)
	
	if ((distance > thresholdDistance) and (angularDifference > thresholdAngle)): return False
	else: return (timeDifference < thresholdTime)



def main():
	global rootNtuple
	
	parser = OptionParser(usage="usage: %prog [options] INPUT_FILE",
			              description="Reduce number of GPS measures without loss of general information.")

	parser.add_option("-o", "--output", help="Output file. Stdout is choosen if no output is specified.")
	parser.add_option("--threshold-distance", default=10.0, type=float, help="Threshold for min. distance between two points in meters. [Default: 10.0]")
	parser.add_option("--threshold-seconds", default=60.0, type=float, help="Threshold for min. difference in time in seconds. [Default: 60.0]")
	parser.add_option("--threshold-angle", default=5.0, type=float, help="Threshold for min. angle spanned by three points in degrees. [Default: 5.0]")
	parser.add_option("--statistics-output", action="store_true", default=False, help="Output statistics. Requires ROOT. [Default: False]")

	(options, args) = parser.parse_args()
	
	if len(args) < 1:
		print "ERROR: no input file specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	if len(args) < 1:
		print "ERROR: to many input files specified!"
		print ""
		parser.print_help()
		sys.exit(1)
	
	gpsDataTree = etree.parse(args[0])
	gpsDataTreeRoot = gpsDataTree.getroot()
	
	def getNsPlusKey(key, nsmap=gpsDataTreeRoot.nsmap, nsmapKey=None): return ("{"+nsmap[nsmapKey]+"}"+key)
	
	trkpt1 = None
	trkpt2 = None
	trkpt3 = None
	trkpt4 = None
	
	if options.statistics_output:
		import ROOT
		rootFile = ROOT.TFile(options.output+".root" if options.output else "gps_data.root", "RECREATE")
		rootNtuple = ROOT.TNtuple("gps_data", "gps_data", "dist:time:angle")
	
	for trkpt in gpsDataTreeRoot.iter(getNsPlusKey("trkpt")):
		trkpt1 = trkpt2
		trkpt2 = trkpt3
		trkpt3 = trkpt4
		trkpt4 = trkpt
		
		removeTrkpt3 = determineRemoveMiddleTrkpt(trkpt2, trkpt3, trkpt4, getNsPlusKey, options.threshold_distance, options.threshold_seconds, options.threshold_angle)
		if removeTrkpt3:
			trkpt3.getparent().remove(trkpt3)
			
			trkpt3 = trkpt2
			trkpt2 = trkpt1
			trkpt1 = None
	
	if options.statistics_output:
		rootFile.Write()
		rootFile.Close()
		
	if options.output: gpsDataTree.write(options.output)
	else: print etree.tostring(gpsDataTreeRoot, pretty_print=True)
	
if __name__ == "__main__": main()

