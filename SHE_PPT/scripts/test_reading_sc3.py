from SHE_PPT import file_io
from SHE_PPT.she_frame_stack import SHEFrameStack
import os.path
import pdb

workdir = "/home/brg/Data/sc3-workdir"

exposure_listfile_name = "CalibratedFrames.json"
stacked_frame_filename = "DpdVisStackedFrame.xml"
detections_listfile_name = "DetectionsCatalogs.json"


frame_stack = SHEFrameStack.read( exposure_listfile_filename = exposure_listfile_name,
                                  stacked_image_product_filename = stacked_frame_filename,
                                  detections_listfile_filename = detections_listfile_name,
                                  workdir = workdir )

cat = frame_stack.detections_catalogue

num_output = 0
i = 0

while num_output < 10:
    row = cat[i]

    i += 1

    ra = row['RightAscension']
    dec = row['Declination']
    
    image_stack = frame_stack.extract_stamp_stack(ra,dec,300,none_if_out_of_bounds=True)

    if image_stack is None:
        continue

    image_stack.stacked_image.header['CEN_XW'] = ra
    image_stack.stacked_image.header['CEN_YW'] = dec

    image_stack.stacked_image.write_to_fits('test_stack_'+str(num_output)+'.fits',clobber=True,data_only=True)
    print("Printed image " + str(num_output) + ".")

    for x in range(4):
        exposure = image_stack.exposures[x]

        if exposure is not None:

            exposure.header['CEN_XW'] = ra
            exposure.header['CEN_YW'] = dec

            exposure.write_to_fits('test_stack_'+str(num_output)+'_'+str(x)+'.fits',clobber=True,data_only=True)
            print("Printed image " + str(num_output)+'_'+str(x) + ".")

    num_output += 1

