# This program is used to calculate the green view index based on the collected metadata. The
# Object based images classification algorithm is used to classify the greenery from the GSV imgs
# in this code, the meanshift algorithm implemented by pymeanshift was used to segment image
# first, based on the segmented image, we further use the Otsu's method to find threshold from
# ExG image to extract the greenery pixels.

# For more details about the object based image classification algorithm
# check: Li et al., 2016, Who lives in greener neighborhoods? the distribution of street greenery and it association
# with residents' socioeconomic conditions in Hartford, Connectictu, USA

# This program implementing OTSU algorithm to chose the threshold automatically
# For more details about the OTSU algorithm and python implementation
# cite: http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html

import time
# from StringIO import StringIO # for python 2.7
from io import BytesIO  # for python 3

import matplotlib.pyplot as plt
import numpy
import requests
from PIL import Image


# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT
# First version June 18, 2014
def graythresh(array, level):
    """
    array: is the numpy array waiting for processing
    return thresh: is the result got by OTSU algorithm
    if the threshold is less than level, then set the level as the threshold
    by Xiaojiang Li
    """

    max_val = numpy.max(array)
    min_val = numpy.min(array)

    # if the inputImage is a float of double dataset then we transform the data
    # in to byte and range from [0 255]
    if max_val <= 1:
        array = array * 255
        # print "New max value is %s" %(numpy.max(array))
    elif max_val >= 256:
        array = numpy.int((array - min_val) / (max_val - min_val))
        # print "New min value is %s" %(numpy.min(array))

    # turn the negative to natural number
    neg_idx = numpy.where(array < 0)
    array[neg_idx] = 0

    # calculate the hist of 'array'
    hist = numpy.histogram(array, range(257))
    p_hist = hist[0] * 1.0 / numpy.sum(hist[0])

    omega = p_hist.cumsum()

    temp = numpy.arange(256)
    mu = p_hist * (temp + 1)
    mu = mu.cumsum()

    n = len(mu)
    mu_t = mu[n - 1]

    sigma_b_squared = (mu_t * omega - mu) ** 2 / (omega * (1 - omega))

    # try to found if all sigma_b squared are NaN or Infinity
    ind_inf = numpy.where(sigma_b_squared == numpy.inf)

    cin = 0
    if len(ind_inf[0]) > 0:
        cin = len(ind_inf[0])

    max_val = numpy.max(sigma_b_squared)

    is_all_inf = cin == 256
    if is_all_inf != 1:
        index = numpy.where(sigma_b_squared == max_val)
        idx = numpy.mean(index)
        threshold = (idx - 1) / 255.0
    else:
        threshold = level

    if numpy.isnan(threshold):
        threshold = level

    return threshold


def image_show(image, nrows=1, ncols=1, cmap='gray'):
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8, 8))
    ax.imshow(image, cmap)
    ax.axis('off')
    return fig, ax


def vegetation_classification(img):
    """
    This function is used to classify the green vegetation from GSV image,
    This is based on object based and otsu automatically thresholding method
    The season of GSV images were also considered in this function
        img: the numpy array image, eg. img = numpy.array(Image.open(StringIO(response.content)))
        return the percentage of the green vegetation pixels in the GSV image

    By Xiaojiang Li
    """

    # import pymeanshift as pms
    #
    # # use the meanshift segmentation algorithm to segment the original GSV image
    # (segmented_image, labels_image, number_regions) = pms.segment(img,spatial_radius=6,
    #                                                  range_radius=7, min_density=40)

    import Segmentor

    segmented_image = Segmentor.segment(img)

    image_norm = segmented_image / 255.0

    red = image_norm[:, :, 0]
    green = image_norm[:, :, 1]
    blue = image_norm[:, :, 2]

    # calculate the difference between green band with other two bands
    green_red_diff = green - red
    green_blue_diff = green - blue

    exg = green_red_diff + green_blue_diff
    diff_img = green_red_diff * green_blue_diff

    red_thre_img_u = red < 0.6
    green_thre_img_u = green < 0.9
    blue_thre_img_u = blue < 0.6

    shadow_red_u = red < 0.3
    shadow_green_u = green < 0.3
    shadow_blue_u = blue < 0.3
    del red, blue, green, image_norm

    gree_img1 = red_thre_img_u * blue_thre_img_u * green_thre_img_u
    green_img_shadow1 = shadow_red_u * shadow_green_u * shadow_blue_u
    del red_thre_img_u, green_thre_img_u, blue_thre_img_u
    del shadow_red_u, shadow_green_u, shadow_blue_u

    gree_img3 = diff_img > 0.0
    gree_img4 = green_red_diff > 0
    threshold = graythresh(exg, 0.1)

    if threshold > 0.1:
        threshold = 0.1
    elif threshold < 0.05:
        threshold = 0.05

    gree_img2 = exg > threshold
    green_img_shadow2 = exg > 0.05
    green_img = gree_img1 * gree_img2 + green_img_shadow2 * green_img_shadow1
    del exg, green_blue_diff, green_red_diff
    del green_img_shadow1, green_img_shadow2

    # image_show(greenImg)
    # plt.show(block=False)
    # plt.pause(1)
    # plt.close()

    # calculate the percentage of the green vegetation
    green_pxl_num = len(numpy.where(green_img != 0)[0])
    green_percent = green_pxl_num / (400.0 * 400) * 100
    del gree_img1, gree_img2
    del gree_img3, gree_img4

    return green_percent


# using 18 directions is too time consuming, therefore, here I only use 6 horizontal directions
# Each time the function will read a text, with 1000 records, and save the result as a single TXT
def green_view_computing_ogr_6horizon(gsv_info_folder, out_txt_root, greenmonth, key_file):
    """
    This function is used to download the GSV from the information provide
    by the gsv info txt, and save the result to a shapefile

    Required modules: StringIO, numpy, requests, and PIL

        gsv_info_folder: the input folder name of GSV info txt
        out_txt_root: the output folder to store result green result in txt files
        greenmonth: a list of the green season, for example in Boston, greenmonth = ['05','06','07','08','09']
        key_file: the API keys in txt file, each key is one row, I prepared five keys, you can replace by your own
        keys if you have Google Account

    last modified by Xiaojiang Li, MIT Senseable City Lab, March 25, 2018

    """

    # read the Google Street View API key files, you can also replace these keys by your own
    lines = open(key_file, "r")
    keylist = []
    for line in lines:
        key = line[:-1]
        keylist.append(key)

    print('The key list is:=============', keylist)

    # set a series of heading angle
    heading_arr = 360 / 6 * numpy.array([0, 1, 2, 3, 4, 5])

    pano_id_done_list = []
    # number of GSV images for Green View calculation, in my original Green View View paper, I used 18 images,
    # in this case, 6 images at different horizontal directions should be good.
    num_gsv_img = len(heading_arr) * 1.0
    pitch = 0

    # create a folder for GSV images and grenView Info
    if not os.path.exists(out_txt_root):
        os.makedirs(out_txt_root)

    # the input GSV info should be in a folder
    if not os.path.isdir(gsv_info_folder):
        print('You should input a folder for GSV metadata')
        return
    else:
        all_txt_files = os.listdir(gsv_info_folder)
        for txt_file in all_txt_files:
            if not txt_file.endswith('.txt'):
                continue

            txt_filename = os.path.join(gsv_info_folder, txt_file)
            lines = open(txt_filename, "r")

            # create empty lists, to store the information of panos, and remove duplicates
            pano_id_lst = []
            pano_date_lst = []
            pano_lon_lst = []
            pano_lat_lst = []

            # loop all lines in the txt files
            for line in lines:
                metadata = line.split(" ")
                pano_id = metadata[1]
                pano_date = metadata[3]
                month = pano_date[-2:]
                lon = metadata[5]
                lat = metadata[7][:-1]

                # print (lon, lat, month, pano_id, pano_date)

                # in case, the longitude and latitude are invalid
                if len(lon) < 3:
                    continue

                # only use the months of green seasons
                if month not in greenmonth:
                    continue
                else:
                    pano_id_lst.append(pano_id)
                    pano_date_lst.append(pano_date)
                    pano_lon_lst.append(lon)
                    pano_lat_lst.append(lat)

            # the output text file to store the green view and pano info
            gv_txt = 'GV_' + os.path.basename(txt_file)
            green_view_txt_file = os.path.join(out_txt_root, gv_txt)

            # check whether the file already generated, if yes, skip. Therefore, you can run several process at
            # same time using this code.
            print(green_view_txt_file)
            if os.path.exists(green_view_txt_file):
                continue

            # write the green view and pano info to txt
            with open(green_view_txt_file, "w") as gv_res_txt:
                for i in range(len(pano_id_lst)):
                    pano_date = pano_date_lst[i]
                    pano_id = pano_id_lst[i]
                    lat = pano_lat_lst[i]
                    lon = pano_lon_lst[i]

                    # avoid multiple GVI calculation for the same panorama id
                    if pano_id in pano_id_done_list:
                        continue

                    pano_id_done_list.append(pano_id)

                    # get a different key from the key list each time
                    # idx = i % len(keylist)
                    # key = keylist[idx]
                    key = 'AIzaSyCmy2XHaiYUfaVvIwQgIenxIPSIJzvJpsA'

                    # calculate the green view index
                    green_percent = 0.0

                    for heading in heading_arr:
                        print("Heading is: ", heading)

                        # using different keys for different process, each key can only request 25,000 imgs every
                        # 24 hours
                        url = "http://maps.googleapis.com/maps/api/streetview?size=400x400&pano=%s&fov=60&" \
                              "heading=%d&pitch=%d&sensor=false&key=%s" % (pano_id, heading, pitch, key)

                        # let the code to pause by 1s, in order to not go over data limitation of Google quota
                        time.sleep(0.01)

                        # classify the GSV images and calcuate the GVI
                        try:
                            response = requests.get(url)
                            im = numpy.array(Image.open(BytesIO(response.content)))
                            percent = vegetation_classification(im)
                            green_percent = green_percent + percent

                        # if the GSV images are not download successfully or failed to run, then return a null value
                        except:
                            print('SOMETHING UNEXPECTED JUST HAPPENED')
                            green_percent = -1000
                            break

                    # calculate the green view index by averaging six percents from six images
                    green_view_val = green_percent / num_gsv_img
                    print('The greenview: %s, pano: %s, (%s, %s)' % (green_view_val, pano_id, lat, lon))

                    # write the result and the pano info to the result txt file
                    line_txt = 'panoID: %s panoDate: %s longitude: %s latitude: %s, greenview: %s\n' % (
                        pano_id, pano_date, lon, lat, green_view_val)
                    gv_res_txt.write(line_txt)


# ------------------------------Main function-------------------------------
if __name__ == "__main__":
    import os.path

    gsv_info_root = '..\\kastela\\metadata'
    output_text_path = '..\\kastela\\GVI_values'
    greenmonth = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    key_file = 'keys.txt'

    green_view_computing_ogr_6horizon(gsv_info_root, output_text_path, greenmonth, key_file)
