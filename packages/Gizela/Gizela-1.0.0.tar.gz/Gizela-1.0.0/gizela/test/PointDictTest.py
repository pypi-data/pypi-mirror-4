"""Unit test for PointDict.py"""

from gizela.data.PointDict import *
from gizela.data.Coord import *
import unittest


class PointDictTestCase(unittest.TestCase):
	def setUp(self):
		self.c1=Coord()
		self.c2=Coord(z=1)
		self.c3=Coord(1,2)
		self.c4=Coord(1,2,3)
		self.c5=Coord(z=1)
		self.c6=Coord(ori=40)

	def tearDown(self):
		pass

	def test_insert_point(self):
		self.assertEqual(self.c2.get_z(), 1)
		self.assertEqual(self.c3.get_x(), 1)
		self.assertEqual(self.c3.get_y(), 2)
		self.assertEqual(self.c4.get_x(), 1)
		self.assertEqual(self.c4.get_y(), 2)
		self.assertEqual(self.c4.get_z(), 3)
		self.assertEqual(self.c5.get_z(), 1)
		self.assertEqual(self.c6.get_ori(), 40)
		self.assertEqual(self.c3.get_xy(), (1,2))
		self.assertEqual(self.c4.get_xyz(), (1,2,3))

	def test_is(self):
		self.assertEqual(self.c1.is_set_z(), False)
		self.assertEqual(self.c1.is_set_xy(), False)
		self.assertEqual(self.c1.is_set_xyz(), False)
		self.assertEqual(self.c2.is_set_z(), True)
		self.assertEqual(self.c2.is_set_xy(), False)
		self.assertEqual(self.c2.is_set_xyz(), False)
		self.assertEqual(self.c3.is_set_z(), False)
		self.assertEqual(self.c3.is_set_xy(), True)
		self.assertEqual(self.c3.is_set_xyz(), False)
		self.assertEqual(self.c4.is_set_z(), True)
		self.assertEqual(self.c4.is_set_xy(), True)
		self.assertEqual(self.c4.is_set_xyz(), True)
		self.assertEqual(self.c5.is_set_z(), True)
		self.assertEqual(self.c5.is_set_xy(), False)
		self.assertEqual(self.c5.is_set_xyz(), False)
		self.assertEqual(self.c1.is_set_ori(), False)
		self.assertEqual(self.c2.is_set_ori(), False)
		self.assertEqual(self.c3.is_set_ori(), False)
		self.assertEqual(self.c4.is_set_ori(), False)
		self.assertEqual(self.c5.is_set_ori(), False)
		self.assertEqual(self.c6.is_set_ori(), True)


	def test_set(self):
		self.c1.set_xy(10,20)
		self.assertEqual(self.c1.get_xy(),(10,20))
		self.c1.set_z(30)
		self.assertEqual(self.c1.get_z(),30)
		self.c2.set_xyz(10,20,30)
		self.assertEqual(self.c2.get_xyz(),(10,20,30))
	
	def test_unused(self):
		self.c4.set_unused()
		self.assertEqual(self.c4.is_fix_xy(), False)
		self.assertEqual(self.c4.is_fix_xyz(), False)
		self.assertEqual(self.c4.is_fix_z(), False)
		self.assertEqual(self.c4.is_adj_xy(), False)
		self.assertEqual(self.c4.is_adj_XY(), False)
		self.assertEqual(self.c4.is_adj_xyz(), False)
		self.assertEqual(self.c4.is_adj_XYZ(), False)
		self.assertEqual(self.c4.is_adj_XYz(), False)
		self.assertEqual(self.c4.is_adj_xyZ(), False)

	def test_set_is_fix_adj_con_unused_active(self):
		self.c1.set_fix_xy()
		self.assertEqual(self.c1.is_fix_xy(), True)
		self.c1.set_fix_z()
		self.assertEqual(self.c1.is_fix_z(), True)
		self.c1.set_fix_xyz()
		self.assertEqual(self.c1.is_fix_xyz(), True)
		
		self.c1.set_adj_xy()
		self.assertEqual(self.c1.is_adj_xy(), True)
		self.c1.set_adj_z()
		self.assertEqual(self.c1.is_adj_z(), True)
		self.c1.set_adj_xyz()
		self.assertEqual(self.c1.is_adj_xyz(), True)
		
		self.c1.set_con_xy()
		self.assertEqual(self.c1.is_con_xy(), True)
		self.c1.set_con_z()
		self.assertEqual(self.c1.is_con_z(), True)
		self.c1.set_adj_xyZ()
		self.assertEqual(self.c1.is_adj_xyZ(), True)
		self.c1.set_adj_XYz()
		self.assertEqual(self.c1.is_adj_XYz(), True)
		self.c1.set_adj_XYZ()
		self.assertEqual(self.c1.is_adj_XYZ(), True)


#class CoordTestSuite(unittest.TestSuite):
#	def __init__(self):
#		caseClass = PointDictTestCase
#		tests = [t for t in dir(caseClass) if t[:5] == 'test']
#		print tests
#	        unittest.TestSuite.__init__(self,map(PointDictTestCase, tests))
#
#def suite():
#    return unittest.makeSuite(PointDictTestCase)
	
	
if __name__ == "__main__":
    unittest.main()
