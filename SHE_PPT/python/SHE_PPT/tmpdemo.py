"""This script gives a small demo of the image object.
"""

import she_image
import numpy as np


size = (50, 50)



array = np.random.randn(size)

mask = np.zeros(size)

a = she_image.SHEImage(array, mask)


