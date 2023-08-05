#!/bin/python

import pgext
import pygame
import time

class Tester:
	def __init__(self,source_image,num=1):
		self.num = num
		self.source = pygame.image.load(source_image)
		self.tests = {}
		self.order = []
		self.results = {}
		self.times_start = {}
		self.times_result = {}
		self.types = ["modify-return","modify-inplace","make"]
		
	def addTests(self, tests):
		for t in tests:
			self.addTest(t)
		
	def addTest(self,test):
		source = self.source
		
		if len(test) == 4:
			name, typ, func, args = test
		else:
			name, typ, func, args, source = test
		
		if not typ in self.types:
			print "Unknown test type: %s"%typ
			return False
		self.tests[name] = ( typ, func, args, source )
		self.order.append(name)
		self.times_result[name] = []
		return True
		
	def saveImage(self,name,image):
		pygame.image.save(image, "out_%s.png"%name)
		
	def meterStart(self,name):
		self.times_start[name] = time.time()
		
	def meterEnd(self,name):
		self.times_result[name].append( (time.time()-self.times_start[name])*1000 )
		
	def doTests(self):
		for n in xrange(self.num):
			for test in self.order:
				self.doTest(test)
			
	def doTest(self,name):
		try:
			test = self.tests[name]
			source = test[3].copy()
			if test[0] == "modify-return":
				self.meterStart(name)
				image = test[1]( source, *test[2] )
				self.meterEnd(name)
				self.saveImage(name,image)
			elif test[0] == "modify-inplace":
				self.meterStart(name)
				test[1]( source, *test[2] )
				self.meterEnd(name)
				self.saveImage(name,source)
			elif test[0] == "make":
				self.meterStart(name)
				image = test[1]( *test[2] )
				self.meterEnd(name)
				self.saveImage(name,image)
			
			self.results[name] = 0
		except Exception,e:
			self.results[name] = e
			
	def printResults(self):
		print "Testing cycles: %s"%self.num
		count = 0
		for test in self.order:
			t = self.times_result[test]
			if self.results[test]:
				print "%s: Error (%s)"%( test, self.results[test] )
			else:
				avgtime = sum(self.times_result[test])/float(len(self.times_result[test]))
				count += avgtime
				print "%21s: %.1f ms"%( test, avgtime )
		print "%21s: %.1f ms"%( "Total time", count )

source_mask = pygame.image.load("source_mask.png")
source_rgb = pygame.image.load("source_rgb.png")

tester = Tester("source.png",10)
tester.addTests([
		("color.colorize", "modify-inplace", pgext.color.colorize, [300,40,-30,50] ),
		("color.greyscale", "modify-inplace", pgext.color.greyscale, []),
		("color.greyscale2", "modify-inplace", pgext.color.greyscale, [1]),
		("color.invert", "modify-inplace", pgext.color.invert, []),
		("color.hue", "modify-inplace", pgext.color.hue, [-50]),
		("color.saturation", "modify-inplace", pgext.color.saturation, [50,2]),
		("color.lightness", "modify-inplace", pgext.color.lightness, [-50]),
		("color.value", "modify-inplace", pgext.color.value, [-50]),
		("color.setColor", "modify-inplace", pgext.color.setColor, [(120,0,200)]),
		("color.alphaMask", "modify-inplace", pgext.color.alphaMask, [source_mask], source_rgb),
		
		("filters.shadow", "modify-return", pgext.filters.shadow, [(0,0,0), 5, 1, 0.9]),
		("filters.blur", "modify-inplace", pgext.filters.blur, [4]),
		("filters.hvBlur-h", "modify-inplace", pgext.filters.hvBlur, [6,0]),
		("filters.hvBlur-v", "modify-inplace", pgext.filters.hvBlur, [6,1]),
		("filters.noise", "modify-inplace", pgext.filters.noise, [55,2]),
		("filters.gradient1", "make", pgext.filters.gradient, [( 200, 200 ), ( 100,100,200 ), (100,200,100), 0, 1.0]),
		("filters.gradient2", "make", pgext.filters.gradient, [( 200, 200 ), ( 255,0,0 ), (0,0,255), 0, 0.3]),
		("filters.gradient3", "make", pgext.filters.gradient, [( 200,200 ), ( 100,0,0 ), (0,55,55), 1, 1.0]),
])
		
tester.doTests()
tester.printResults()