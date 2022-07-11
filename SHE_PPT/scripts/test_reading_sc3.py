# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

from timeit import default_timer as timer

from SHE_PPT.she_frame_stack import SHEFrameStack

workdir = "/home/brg/Data/sc3-workdir"

exposure_listfile_name = "CalibratedFrames.json"
stacked_frame_filename = "DpdVisStackedFrame.xml"

exposure_segmentation_maps_listfile_name = "MosaicFrames.json"
stacked_frame_mosaic_filename = "EUC_SHE_SHE_Mosaic_Stack_2018315T15328.0Z_00.00.fits"

detections_listfile_name = "DetectionsCatalogs.json"

start = timer()

frame_stack = SHEFrameStack.read(exposure_listfile_filename = exposure_listfile_name,
                                 seg_listfile_filename = exposure_segmentation_maps_listfile_name,
                                 stacked_image_product_filename = stacked_frame_filename,
                                 stacked_seg_filename = stacked_frame_mosaic_filename,
                                 detections_listfile_filename = detections_listfile_name,
                                 workdir = workdir)

stop = timer()

print("Time elapsed for reading: " + str((stop - start)))

exit()

cat = frame_stack.detections_catalogue

num_output = 0
i = 0

while num_output < 10:
    row = cat[i]

    i += 1

    ra = row['RightAscension']
    dec = row['Declination']

    image_stack = frame_stack.extract_stamp_stack(ra, dec, 300, none_if_out_of_bounds = True)

    if image_stack is None:
        continue

    image_stack.stacked_image.header['CEN_XW'] = ra
    image_stack.stacked_image.header['CEN_YW'] = dec

    image_stack.stacked_image.write_to_fits('test_stack_' + str(num_output) + '.fits', overwrite = True,
                                            data_only = False)
    print("Printed image " + str(num_output) + ".")

    for x in range(4):
        exposure = image_stack.exposures[x]

        if exposure is not None:

            exposure.header['CEN_XW'] = ra
            exposure.header['CEN_YW'] = dec

            exposure.write_to_fits('test_stack_' + str(num_output) + '_' +
                                   str(x) + '.fits', overwrite = True, data_only = False)
            print("Printed image " + str(num_output) + '_' + str(x) + ".")

    num_output += 1
