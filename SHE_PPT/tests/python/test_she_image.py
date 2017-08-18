"""This script gives a small demo of the image object.
"""

import she_image
import numpy as np


size = 50



array = np.random.randn(size**2).reshape((size, size))

mask = np.zeros(size**2).reshape((size, size))

a = she_image.SHEImage(array, mask)




print(a)