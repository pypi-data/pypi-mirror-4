#!/bin/env python

import pgext
import pygame
import time

pygame.display.init()
pygame.display.set_mode((1, 1))


class Tester:
    def __init__(self, source_image, num=1):
        self.num = num
        self.source = pygame.image.load(source_image)
        self.tests = {}
        self.order = []
        self.results = {}
        self.result_surfaces = {}
        self.times_start = {}
        self.times_result = {}
        self.types = ["modify-return", "modify-inplace", "make"]

    def addTests(self, tests):
        for t in tests:
            self.addTest(t)

    def addTest(self, test):
        source = self.source

        if len(test) == 4:
            name, typ, func, args = test
        else:
            name, typ, func, args, source = test

        if not typ in self.types:
            print "Unknown test type: %s" % typ
            return False
        self.tests[name] = (typ, func, args, source)
        self.order.append(name)
        self.times_result[name] = []
        return True

    def saveImage(self, name, image):
        self.result_surfaces[name] = image

    def saveAll(self):
        for name in self.result_surfaces:
            image = self.result_surfaces[name]
            pygame.image.save(image, "out_%s.png" % name)

    def meterStart(self, name):
        self.times_start[name] = time.time()

    def meterEnd(self, name):
        self.times_result[name].append((time.time() -
                                       self.times_start[name]) * 1000)

    def doTests(self):
        for n in xrange(self.num):
            for test in self.order:
                self.doTest(test)
        self.saveAll()

    def doTest(self, name):
        print "%sTest: %s" % ("\b"*80, name),
        try:
            test = self.tests[name]
            source = test[3].copy()
            if test[0] == "modify-return":
                self.meterStart(name)
                image = test[1](source, *test[2])
                self.meterEnd(name)
                self.saveImage(name, image)
            elif test[0] == "modify-inplace":
                self.meterStart(name)
                test[1](source, *test[2])
                self.meterEnd(name)
                self.saveImage(name, source)
            elif test[0] == "make":
                self.meterStart(name)
                image = test[1](*test[2])
                self.meterEnd(name)
                self.saveImage(name, image)

            self.results[name] = 0
        except Exception, e:
            self.results[name] = e

    def printResults(self):
        print "Testing cycles: %s" % self.num
        count = 0
        for test in self.order:
            t = self.times_result[test]
            if self.results[test]:
                print "%s: Error (%s)" % (test, t)
            else:
                avgtime = sum(t) / float(len(t))
                count += avgtime
                print "%21s: %.1f ms" % (test, avgtime)
        print "%21s: %.1f ms" % ("Total time", count)

source_rgb = pygame.image.load("source_rgb.png").convert()
source_rgba = pygame.image.load("source_rgba.png")
source_mask = pygame.image.load("source_mask.png")
source_colorize = pygame.image.load("source_colorize.png")

tester = Tester("source_rgb.png", 10)

tester.addTests([
                ("color.colorize", "modify-inplace",
                 pgext.color.colorize, [120, 0, -30, 10], source_colorize),
                ("color.greyscale1", "modify-inplace",
                 pgext.color.greyscale, []),
                ("color.greyscale2", "modify-inplace",
                 pgext.color.greyscale, [1]),
                ("color.greyscale3", "modify-inplace",
                 pgext.color.greyscale, [2]),
                ("color.invert", "modify-inplace", pgext.color.invert, []),
                ("color.hue", "modify-inplace", pgext.color.hue, [80]),
                ("color.saturation", "modify-inplace",
                 pgext.color.saturation, [30, 2]),
                ("color.lightness", "modify-inplace",
                 pgext.color.lightness, [20]),
                ("color.value", "modify-inplace", pgext.color.value, [-50]),
                ("color.multiply1", "modify-inplace",
                 pgext.color.multiply, [2.5]),
                ("color.multiply2", "modify-inplace",
                 pgext.color.multiply, [0.4]),
                ("color.multiply3", "modify-inplace",
                 pgext.color.multiply, [0.0, 1, 0, 1]),
                ("color.setColor", "modify-inplace",
                 pgext.color.setColor, [(120, 0, 200)], source_rgba),
                ("color.setAlpha", "modify-inplace",
                 pgext.color.setAlpha, [40, 2], source_rgba),
                ("color.alphaMask", "modify-inplace",
                 pgext.color.alphaMask, [source_mask]),
                ("color.alphaMask2", "modify-inplace",
                 pgext.color.alphaMask, [source_rgba, 1]),


                ("filters.shadow", "modify-return",
                 pgext.filters.shadow, [(0, 0, 0), 5, 1, 0.9], source_rgba),
                ("filters.shadow2", "modify-return",
                 pgext.filters.shadow, [(200, 0, 0), 5, 1, 0.9], source_rgba),
                ("filters.blur", "modify-inplace", pgext.filters.blur, [4]),
                ("filters.hvBlur-h", "modify-inplace",
                 pgext.filters.hvBlur, [6, 0]),
                ("filters.hvBlur-v", "modify-inplace",
                 pgext.filters.hvBlur, [6, 1]),
                ("filters.noise", "modify-inplace",
                 pgext.filters.noise, [55, 2]),
                ("filters.noiseBlur1", "modify-inplace",
                 pgext.filters.noiseBlur, [5]),
                ("filters.noiseBlur2", "modify-inplace",
                 pgext.filters.noiseBlur, [20, 1]),
                ("filters.scratch", "modify-inplace",
                 pgext.filters.scratch, [5]),
                ("filters.pixelize", "modify-inplace",
                 pgext.filters.pixelize, [10]),

                ("filters.gradient1", "make", pgext.filters.gradient,
                 [(200, 200), (100, 100, 200), (100, 200, 100), 0, 1.0]),
                ("filters.gradient2", "make", pgext.filters.gradient,
                 [(200, 200), (255, 0, 0, 0), (0, 0, 255, 255), 0, 0.3]),
                ("filters.gradient3", "make", pgext.filters.gradient,
                 [(200, 200), (100, 0, 0), (0, 55, 55), 1, 1.0]),
                ])

tester.doTests()
tester.printResults()
