import unittest
from selector import BrewSelector
from brew import *
from collections import defaultdict

class SelectorTest(unittest.TestCase):
	
	def setUp(self):
		self.empty_bs=BrewSelector(empty=True)
		self.brew_9=Brew('sequential', ['#F7FCFD', '#E5F5F9', '#CCECE6','#99D8C9', '#66C2A4', '#41AE76', '#238B45', '#006D2C', '#00441B'], 'BuGn', colorblind_safe=True)
		self.bs=BrewSelector()

	def test_add_brew(self):
		self.empty_bs.add_brew(self.brew_9)
		self.assertEqual(self.empty_bs.brews, {'sequential':{9:{'BuGn':self.brew_9}}, 'diverging': defaultdict(dict), 'qualitative': defaultdict(dict)})

	def test_get_brew(self):
		self.assertEqual(self.bs.get_brew('sequential', 9, 'BuGn'), self.brew_9)

	def test_list_schemes_sequential(self):
		self.assertEqual(sorted(self.bs.list_schemes('sequential', 9)), sorted(('BuGn', 'BuPu', 'GnBu','OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'RdPu', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'Blues', 'Greens', 'Greys', 'Oranges', 'Purples', 'Reds')))
	
	def test_list_schemes_qualitative(self):
		self.assertEqual(sorted(self.bs.list_schemes('qualitative', 5)), sorted(('Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3')))

	def test_list_schemes_diverging(self):
		self.assertEqual(sorted(self.bs.list_schemes('diverging', 3)), sorted(('BrBG', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral')))	

	def test_get_colorblind_safe(self):
		self.assertEqual(sorted(self.bs.list_schemes('qualitative', 3, colorblind_safe=True)), sorted(('Dark2', 'Paired', 'Set2')))

	def test_get_photocopy_safe(self):
		schemes=self.bs.list_schemes('sequential', 4, photocopy_safe=True)
		self.assertEqual(schemes, ('OrRd',))

	def test_get_print_safe(self):
		schemes=self.bs.list_schemes('sequential', 5, print_safe=True)
		self.assertEqual(sorted(schemes), sorted(('GnBu','PuRd', 'YlGnBu')))


class BrewTest(unittest.TestCase):

	def setUp(self):
		self.brew_9=Brew('sequential', ['#F7FCFD', '#E5F5F9', '#CCECE6','#99D8C9', '#66C2A4', '#41AE76', '#238B45', '#006D2C', '#00441B'], 'BuGn', colorblind_safe=True)
		self.brew_8=Brew('sequential', ['#F7FCFD', '#E5F5F9', '#CCECE6','#99D8C9', '#66C2A4', '#41AE76', '#238B45', '#005824'], 'BuGn', colorblind_safe=True)
		self.brew_7=Brew('sequential', ['#EDF8FB', '#CCECE6', '#99D8C9', '#66C2A4', '#41AE76', '#238B45', '#005824'], 'BuGn', colorblind_safe=True)
		self.brew_6=Brew('sequential', ['#EDF8FB', '#CCECE6', '#99D8C9', '#66C2A4', '#2CA25F', '#006D2C'], 'BuGn', colorblind_safe=True)
		self.brew_5=Brew('sequential', ['#EDF8FB', '#B2E2E2', '#66C2A4', '#2CA25F', '#006D2C'], 'BuGn', colorblind_safe=True)
		self.brew_4=Brew('sequential', ['#EDF8FB', '#B2E2E2', '#66C2A4', '#238B45'], 'BuGn', colorblind_safe=True, print_safe=True)
		self.brew_3=Brew('sequential', ['#E5F5F9', '#99D8C9', '#2CA25F'], 'BuGn', colorblind_safe=True, photocopy_safe=True, print_safe=True)
		self.BuGn=['#F7FCFD', '#EDF8FB', '#E5F5F9', '#CCECE6', '#B2E2E2', '#99D8C9', '#66C2A4', '#41AE76','#2CA25F', '#238B45', '#006D2C', '#005824', '#00441B']

	def test_rgb_to_hex(self):
		self.assertEqual('#FFFFFF', rgb_to_hex((255, 255, 255)))
		self.assertEqual('#FDD49E', rgb_to_hex((253, 212, 158)))

	def test_hex_to_rgb(self):
		self.assertEqual(hex_to_rgb('#FFFFFF'), (255, 255, 255))
		self.assertEqual(hex_to_rgb('#FDD49E'), (253, 212, 158))

	def test_sequential_scheme_builder(self):
		self.assertEqual(sequential_from_scheme(self.BuGn, 9), self.brew_9.colors)
		self.assertEqual(sequential_from_scheme(self.BuGn, 8), self.brew_8.colors)
		self.assertEqual(sequential_from_scheme(self.BuGn, 7), self.brew_7.colors)
		self.assertEqual(sequential_from_scheme(self.BuGn, 6), self.brew_6.colors)
		self.assertEqual(sequential_from_scheme(self.BuGn, 5), self.brew_5.colors)
		self.assertEqual(sequential_from_scheme(self.BuGn, 4), self.brew_4.colors)
		self.assertEqual(sequential_from_scheme(self.BuGn, 3), self.brew_3.colors)

if __name__=='__main__':
	unittest.main()