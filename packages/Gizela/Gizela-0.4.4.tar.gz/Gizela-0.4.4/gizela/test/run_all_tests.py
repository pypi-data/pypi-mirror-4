#!/usr/bin/env python

# $Id: run_all_tests.py 9 2010-04-19 13:57:04Z kubin $

import unittest

def suite():
	modules_to_test = ('TextTableTest',
			'PointDictTest',
			'GamaLocalAdjustmentParserTest',
			'DisplacementTest')
	alltests = unittest.TestSuite()
	for module in map(__import__, modules_to_test):
		#print module
		alltests.addTest(unittest.findTestCases(module))
	return alltests

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
