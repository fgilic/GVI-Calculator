from skimage import io
import numpy as np
import matplotlib.pyplot as plt

import skimage.data as data
import skimage.segmentation as seg
import skimage.filters as filters
import skimage.draw as draw
import skimage.color as color

def image_show(image, nrows=1, ncols=1, cmap='gray'):
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8,8))
    ax.imshow(image, cmap='gray')
    ax.axis('off')
    return fig, ax

def segment(image):
    # image = io.imread(img)
    # image_show(image)
    # plt.show(block=False)
    # plt.pause(1)
    # plt.close()
    # image_slic = seg.slic(image,n_segments=500)

    image_felzenszwalb = seg.felzenszwalb(image)
    image_felzenszwalb_colored = color.label2rgb(image_felzenszwalb, image, kind='avg')
    # image_show(image_felzenszwalb_colored);

    # image_show(color.label2rgb(image_slic, image, kind='avg'));
    # plt.show(block=False)
    # plt.pause(1)
    # plt.close()

    return image_felzenszwalb_colored
