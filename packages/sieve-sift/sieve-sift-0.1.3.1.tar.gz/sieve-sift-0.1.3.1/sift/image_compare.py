#encoding:utf-8
import StringIO
import tempfile
import urllib


from PIL import Image
from numpy import ndarray

from sift import match, read_features_from_file, process_image


class ImageCompare:
    def __init__(self, image_path_1, image_path_2):
        self.image_path_1 = image_path_1
        self.image_path_2 = image_path_2

        self.loc1, self.desc1 = self.load_key_points(self.image_path_1)
        self.loc2, self.desc2 = self.load_key_points(self.image_path_2)

    def compare(self):
        """
        Compare two image and return the percentage of match
        """

        if isinstance(self.desc1, list):
            self.desc1 = ndarray.array(self.desc1)
        if isinstance(self.desc2, list):
            self.desc2 = ndarray.array(self.desc2)

        #Get the number of the keypoints in each image
        match_master = match(self.desc1, self.desc1)
        match_points_im1 = len(match_master)

        match_master = match(self.desc2, self.desc2)
        match_points_im2 = len(match_master)

        min_key_points = min(match_points_im1, match_points_im2)
        match_points = match(self.desc1, self.desc2)

        count_match_points = 0
        for point in match_points:
            if point[0] != 0:
                count_match_points += 1

        return float(count_match_points) / float(min_key_points)

    def load_key_points(self, image_path):
        """
        Load a image from a url or a local path and process the image using sift
        @return: loc, description
        """
        with tempfile.NamedTemporaryFile() as imagefile, tempfile.NamedTemporaryFile() as siftfile:
            try:
                if "http" in image_path.strip():
                    fd = urllib.urlopen(image_path)
                    image = Image.open(StringIO.StringIO(fd.read()))

                else:
                    image = Image.open(image_path)
            except:
                return None, None

            # Store the images in B/W Int format
            image = image.convert("L")
            image.save(imagefile.name, "PPM")
            imagefile.flush()

            process_image(imagefile.name, siftfile.name)
            loc, description = read_features_from_file(siftfile.name)

            return loc, description
