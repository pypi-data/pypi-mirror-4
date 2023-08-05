import imageresizer.arbo
import unittest

class MyTestCase(unittest.TestCase):

    def test_arbo(self):
        l = imageresizer.arbo.list_dir("/home/mathieu/test")
        self.assertEqual(l, ["", "a/b"])

    def test_arbo_with_slash(self):
        l = imageresizer.arbo.list_dir("/home/mathieu/test/")
        self.assertEqual(l, ["", "a/b"])

    def test_browse(self):
        l = list(imageresizer.arbo.browse("/home/mathieu/test", "/tmp/"))
        self.assertEqual(l,[
            ("/home/mathieu/test/a.jpg", "/tmp/"),
            ("/home/mathieu/test/a/b/b.jpg", "/tmp/a/b")])
