#encoding:utf-8
import os.path
import unittest

from ..image_compare import ImageCompare


class TestSIFTVLFeat(unittest.TestCase):

    def test_compare_equal(self):
        image1 = image2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug.png")
        comparator = ImageCompare(image1, image2)

        compare = comparator.compare()

        self.assertAlmostEqual(compare, 1, places=2)

    def test_compare_rotation(self):
        image1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug.png")
        image2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug_90.png")
        comparator = ImageCompare(image1, image2)

        compare = comparator.compare()

        self.assertGreaterEqual(compare, 0.2)

    def test_compare_smaller(self):
        image1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug.png")
        image2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug_smaller.png")
        comparator = ImageCompare(image1, image2)

        compare = comparator.compare()

        self.assertGreaterEqual(compare, 0.2)


if __name__ == '__main__':
    unittest.main()

