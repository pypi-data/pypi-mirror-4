"""Unit test for GamaLocalAdjustmentParser.py"""

from gizela.xml.GamaLocalAdjustmentParser import GamaLocalAdjustmentParser
import unittest


class GamaLocalAdjustmentParserTest(unittest.TestCase):
	str="""<?xml version="1.0" ?>
<!DOCTYPE gama-local-adjustment SYSTEM "gama-local-adjustment.dtd">

<gama-local-adjustment version="0.5">

<description>
ABC
CBA
</description>

<network-general-parameters
   gama-local-version="1.9.05"
   gama-local-algorithm="svd"
   gama-local-compiler="GNU g++"
   epoch="0.0000000"
   axes-xy="sw"
   angles="right-handed"
/>

<network-processing-summary>

<coordinates-summary>
   <coordinates-summary-adjusted>    <count-xyz>1</count-xyz> <count-xy>2</count-xy> <count-z>3</count-z> </coordinates-summary-adjusted>
   <coordinates-summary-constrained> <count-xyz>4</count-xyz> <count-xy>5</count-xy> <count-z>6</count-z> </coordinates-summary-constrained>
   <coordinates-summary-fixed>       <count-xyz>7</count-xyz> <count-xy>8</count-xy> <count-z>9</count-z> </coordinates-summary-fixed>
</coordinates-summary>

<observations-summary>
   <distances>10</distances>
   <directions>20</directions>
   <angles>30</angles>
   <xyz-coords>40</xyz-coords>
   <h-diffs>50</h-diffs>
   <z-angles>60</z-angles>
   <s-dists>70</s-dists>
   <vectors>80</vectors>
</observations-summary>

<project-equations>
   <equations>100</equations>
   <unknowns>200</unknowns>
   <degrees-of-freedom>300</degrees-of-freedom>
   <defect>400</defect>
   <sum-of-squares >1.1e-01</sum-of-squares >
   <connected-network/>
</project-equations>

<standard-deviation>
   <apriori>1.0000000e+00</apriori>
   <aposteriori>2.0000000e-01</aposteriori>
   <used>apriori</used>

   <probability>0.950</probability>
   <!-- no test for apriori standard deviation -->
   <ratio>1.000</ratio>
   <lower>0.000</lower>
   <upper>0.000</upper>
   <passed/>

   <confidence-scale >2.2e+00</confidence-scale >
</standard-deviation>

</network-processing-summary>

<coordinates>

<fixed>
   <point> <id>A</id> <z>3.3</z> </point>
   <point> <id>AA</id> <x>1.1</x> <y>2.2</y> </point>
   <point> <id>AAA</id> <x>1.1</x> <y>2.2</y> <z>3.3</z> </point>
</fixed>

<approximate>
   <point> <id>A</id> <z>3.3</z> </point>
   <point> <id>B</id> <Z>3.3</Z> </point>
   <point> <id>AA</id> <x>1.1</x> <y>2.2</y> </point>
   <point> <id>BB</id> <X>1.1</X> <Y>2.2</Y> </point>
   <point> <id>AAA</id> <x>1.1</x> <y>2.2</y> <z>3.3</z> </point>
   <point> <id>AAB</id> <x>1.1</x> <y>2.2</y> <Z>3.3</Z> </point>
   <point> <id>BBA</id> <X>1.1</X> <Y>2.2</Y> <z>3.3</z> </point>
   <point> <id>BBB</id> <X>1.1</X> <Y>2.2</Y> <Z>3.3</Z> </point>
</approximate>

<!-- capital X,Y,Z denote constrained coordinates -->
<adjusted>
   <point> <id>A</id> <z>3.3</z> </point>
   <point> <id>B</id> <Z>3.3</Z> </point>
   <point> <id>AA</id> <x>1.1</x> <y>2.2</y> </point>
   <point> <id>BB</id> <X>1.1</X> <Y>2.2</Y> </point>
   <point> <id>AAA</id> <x>1.1</x> <y>2.2</y> <z>3.3</z> </point>
   <point> <id>AAB</id> <x>1.1</x> <y>2.2</y> <Z>3.3</Z> </point>
   <point> <id>BBA</id> <X>1.1</X> <Y>2.2</Y> <z>3.3</z> </point>
   <point> <id>BBB</id> <X>1.1</X> <Y>2.2</Y> <Z>3.3</Z> </point>
</adjusted>

<orientation-shifts>
   <orientation> <id>A</id> <approx>10.1</approx> <adj>20.2</adj> </orientation>
   <orientation> <id>B</id> <approx>10.1</approx> <adj>20.2</adj> </orientation>
</orientation-shifts>

<!-- upper part of symmetric matrix band by rows -->
<cov-mat>
<dim>4</dim> <band>1</band>
<flt>1.1e+00</flt> <flt>1.1e+00</flt>
<flt>2.2e+00</flt> <flt>2.2e+00</flt>
<flt>3.3e+00</flt> <flt>3.3e+00</flt>
<flt>4.4e+00</flt>
</cov-mat>

<!-- original indexes from the adjustment -->
<original-index>
<ind>1</ind>
<ind>2</ind>
<ind>3</ind>
</original-index>

</coordinates>

<observations>

<direction> <from>4001</from> <to>ABC</to>
   <obs>53.3784000</obs> <adj>53.3784000</adj> <stdev>10.000</stdev>
   <qrr>0.000</qrr> <f>0.000</f>
   </direction>
<direction> <from>4001</from> <to>4002</to>
   <obs>259.4313000</obs> <adj>259.4313000</adj> <stdev>10.000</stdev>
   <qrr>0.000</qrr> <f>0.000</f>
   </direction>
<distance> <from>4001</from> <to>4002</to>
   <obs>95.472620</obs> <adj>95.472105</adj> <stdev>1.549</stdev>
   <qrr>2.400</qrr> <f>29.289</f> <std-residual>0.332</std-residual>
   <err-obs>-1.030</err-obs> <err-adj>-0.515</err-adj>
   </distance>
<distance> <from>4002</from> <to>4001</to>
   <obs>95.471590</obs> <adj>95.472105</adj> <stdev>1.549</stdev>
   <qrr>2.400</qrr> <f>29.289</f> <std-residual>0.332</std-residual>
   <err-obs>1.030</err-obs> <err-adj>0.515</err-adj>
   </distance>

</observations>

</gama-local-adjustment>"""

	str2="""<?xml version="1.0" ?>
<!DOCTYPE gama-local-adjustment SYSTEM "gama-local-adjustment.dtd">

<gama-local-adjustment version="0.5">

<project-equations>
   <equations>100</equations>
   <unknowns>200</unknowns>
   <degrees-of-freedom>300</degrees-of-freedom>
   <defect>400</defect>
   <sum-of-squares >1.1e-01</sum-of-squares >
   <disconnected-network/>
</project-equations>

<standard-deviation>
   <apriori>1.0000000e+00</apriori>
   <aposteriori>2.0000000e-01</aposteriori>
   <used>apriori</used>

   <probability>0.950</probability>
   <!-- no test for apriori standard deviation -->
   <ratio>1.000</ratio>
   <lower>0.000</lower>
   <upper>0.000</upper>
   <failed/>

   <confidence-scale >2.2e+00</confidence-scale >
</standard-deviation>

</gama-local-adjustment>"""

	def test_start(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)
		
		self.assertEqual(parser.adjustment['gama-local-adjustment-version'],"0.5")
		
		self.assertEqual(parser.adjustment['description'],"ABC\nCBA")
		
		self.assertEqual(parser.adjustment['network-general-parameters-gama-local-version'],"1.9.05")
		self.assertEqual(parser.adjustment['network-general-parameters-gama-local-algorithm'],"svd")
		self.assertEqual(parser.adjustment['network-general-parameters-gama-local-compiler'],"GNU g++")
		self.assertEqual(parser.adjustment['network-general-parameters-epoch'],"0.0000000")
		self.assertEqual(parser.adjustment['network-general-parameters-axes-xy'],"sw")
		self.assertEqual(parser.adjustment['network-general-parameters-angles'],"right-handed")

	def test_coordinates(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)
		
		self.assertEqual(parser.adjustment['coordinates-summary-adjusted-count-xyz'],1)
		self.assertEqual(parser.adjustment['coordinates-summary-adjusted-count-xy'],2)
		self.assertEqual(parser.adjustment['coordinates-summary-adjusted-count-z'],3)
		self.assertEqual(parser.adjustment['coordinates-summary-constrained-count-xyz'],4)
		self.assertEqual(parser.adjustment['coordinates-summary-constrained-count-xy'],5)
		self.assertEqual(parser.adjustment['coordinates-summary-constrained-count-z'],6)
		self.assertEqual(parser.adjustment['coordinates-summary-fixed-count-xyz'],7)
		self.assertEqual(parser.adjustment['coordinates-summary-fixed-count-xy'],8)
		self.assertEqual(parser.adjustment['coordinates-summary-fixed-count-z'],9)
	
	def test_observations_summary(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)

		self.assertEqual(parser.adjustment['observations-summary-distances'],10)
		self.assertEqual(parser.adjustment['observations-summary-directions'],20)
		self.assertEqual(parser.adjustment['observations-summary-angles'],30)
		self.assertEqual(parser.adjustment['observations-summary-xyz-coords'],40)
		self.assertEqual(parser.adjustment['observations-summary-h-diffs'],50)
		self.assertEqual(parser.adjustment['observations-summary-z-angles'],60)
		self.assertEqual(parser.adjustment['observations-summary-s-dists'],70)
		self.assertEqual(parser.adjustment['observations-summary-vectors'],80)
	
	def test_observations_summary(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)

		self.assertEqual(parser.adjustment['project-equations-equations'],100)
		self.assertEqual(parser.adjustment['project-equations-unknowns'],200)
		self.assertEqual(parser.adjustment['project-equations-degrees-of-freedom'],300)
		self.assertEqual(parser.adjustment['project-equations-defect'],400)
		self.assertEqual(parser.adjustment['project-equations-sum-of-squares'],0.11)

	def test_standard_deviation(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)

		self.assertEqual(parser.adjustment['standard-deviation-apriori'],1)
		self.assertEqual(parser.adjustment['standard-deviation-aposteriori'],0.2)
		self.assertEqual(parser.adjustment['standard-deviation-used'],'apriori')
		self.assertEqual(parser.adjustment['standard-deviation-probability'],0.950)
		self.assertEqual(parser.adjustment['standard-deviation-ratio'],1.000)
		self.assertEqual(parser.adjustment['standard-deviation-lower'],0.000)
		self.assertEqual(parser.adjustment['standard-deviation-upper'],0.000)
		self.assertEqual(parser.adjustment['standard-deviation-confidence-scale'],2.2)

	def test_coordinates_shifts(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)
		#print parser.adjustment['fixed']
		#print parser.adjustment['adjusted']
		#print parser.adjustment['approximate']

		#approximate='''           A                                  3.300  adj_z      
#       A-ori                                 10.100  orientation
#          AA        1.100        2.200               adj_xy     
#         AAA        1.100        2.200        3.300  adj_xyz    
#         AAB        1.100        2.200        3.300  adj_xyZ    
#           B                                  3.300  adj_Z      
#       B-ori                                 10.100  orientation
#          BB        1.100        2.200               adj_XY     
#         BBA        1.100        2.200        3.300  adj_XYz    
#         BBB        1.100        2.200        3.300  adj_XYZ    '''
#		self.assertEqual(parser.adjustment['approximate'].__str__(), approximate)
#		adjusted='''           A                                  3.300  adj_z      
#       A-ori                                 20.200  adj_z      
#          AA        1.100        2.200               adj_xy     
#         AAA        1.100        2.200        3.300  adj_xyz    
#         AAB        1.100        2.200        3.300  adj_xyZ    
#           B                                  3.300  adj_Z      
#       B-ori                                 20.200  adj_z      
#          BB        1.100        2.200               adj_XY     
#         BBA        1.100        2.200        3.300  adj_XYz    
#         BBB        1.100        2.200        3.300  adj_XYZ    '''
#		self.assertEqual(parser.adjustment['adjusted'].__str__(), adjusted)
#		
#		fixed='''           A                                  3.300  adj_z      
#          AA        1.100        2.200               adj_xy     
#         AAA        1.100        2.200        3.300  adj_xyz    '''
#		self.assertEqual(parser.adjustment['fixed'].__str__(), fixed)

	def test_cov_mat(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)
	 	
		self.assertEqual(parser.adjustment['adjusted'].covmat.get_dim(),4)
		self.assertEqual(parser.adjustment['adjusted'].covmat.get_band(),1)
		self.assertEqual(parser.adjustment['adjusted'].covmat.data,[[1.1, 1.1], [2.2, 2.2], [3.3, 3.3], [4.4]])

	def test_connected_passed_true(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str)
		
		self.assertEqual(parser.adjustment['project-equations-connected-network'],True)
		self.assertEqual(parser.adjustment['standard-deviation-passed'],True)
	
	def test_connected_passed_false(self):
		parser=GamaLocalAdjustmentParser.GamaLocalAdjustmentParser()
		parser.parse_string(self.str2)
		
		self.assertEqual(parser.adjustment['project-equations-connected-network'],False)
		self.assertEqual(parser.adjustment['standard-deviation-passed'],False)

if __name__ == "__main__":
    unittest.main()
