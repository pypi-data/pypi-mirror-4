import imageresizer.arbo
import unittest

class MyTestCase(unittest.TestCase):

	def test_arbo(self):
		l = imageresizer.arbo.list_dir("/home/mathieu/test")
		self.assertEqual(l, ["", "a/b"])
