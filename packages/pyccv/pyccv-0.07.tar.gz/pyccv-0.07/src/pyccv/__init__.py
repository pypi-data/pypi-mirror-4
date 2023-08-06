#-*- coding: utf-8 -*-
from ctypes import POINTER
from ctypes import pointer
from ctypes import Structure
from ctypes import c_ubyte
from ctypes import c_int
from ctypes import c_void_p

import numpy as np
import os
import Image
import ImageFilter
from scipy.ndimage import filters

ccvfolder = os.path.abspath(__file__).rsplit(os.path.sep, 1)[0]
ccvname = "_ccv"
libccv = np.ctypeslib.load_library(ccvname, ccvfolder)

class RGBImage(Structure):
    _fields_ = [
        ("width", c_int),
        ("height", c_int),
        ("r", POINTER(c_ubyte)),
        ("g", POINTER(c_ubyte)),
        ("b", POINTER(c_ubyte)),
    ]

#libccv.calc_ccv
libccv.calc_ccv.argtypes = [POINTER(RGBImage), c_int]
libccv.calc_ccv.restype = c_void_p
libccv.delete_ptr.argtypes = [c_void_p]
libccv.destructive_reduce_colors.argtypes = [POINTER(RGBImage)]

def gaussian_kernel(x):
    def pascals_triangle(x):
        last = [1]
        for i in range(1,x):
            r = range(len(last)-1)
            last = [1]+[sum(last[i:i+2]) for i in r]+[1]
        return last
    pt = [pascals_triangle(x)]
    pt = np.array(pt)
    ret = (pt*pt.T).reshape(1,x*x)
    return ret[0]

class Gaussian(ImageFilter.BuiltinFilter):
    name = "Gaussian"
    ksize = 5
    kernel = gaussian_kernel(ksize)
    filterargs = (ksize, ksize), kernel.sum(), 0, kernel.tolist()

def from_pil(pimg):
    pimg = pimg.convert(mode='RGB')
    nimg = np.asarray(pimg)
    nimg.flags.writeable = True
    return nimg

def to_pil(nimg):
    return Image.fromarray(np.uint8(nimg))

def __preprocess(img):
    import cv
    cv_img = cv.CreateImageHeader(img.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_img, img.tostring())
    cv_img2 = cv.CreateImageHeader(img.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_img2, img.tostring())
    #ガウシアンフィルタを掛ける
    cv.Smooth(cv_img, cv_img2, cv.CV_GAUSSIAN,9)
    ary = np.fromstring(
        cv_img2.tostring(),
        dtype=np.uint8,
        count=cv_img2.width*cv_img2.height*cv_img2.nChannels)
    ary.shape = (cv_img2.height,cv_img2.width,cv_img2.nChannels)
    rgbmatrix = ary.transpose(2, 0, 1)
    return np.ascontiguousarray(rgbmatrix,dtype=np.uint8)

def __preprocess_scipy(img,sigma=1.8):
    img = from_pil(img)
    im2 = np.zeros(img.shape)
    for i in range(3):
        im2[:,:,i] = filters.gaussian_filter(img[:,:,i],sigma)
    return np.ascontiguousarray(im2.transpose(2, 0, 1),dtype=np.uint8)

def __preprocess_pil(img,sigma=1.8):
    img = img.filter(Gaussian)
    return np.ascontiguousarray(from_pil(img).transpose(2, 0, 1),dtype=np.uint8)



def calc_ccv(pilimg,size,threashold):
    pilimg = pilimg.convert(mode='RGB')
    pilimg.thumbnail((size, size), Image.ANTIALIAS)
    rgbmatrix = __preprocess_scipy(pilimg)
    ccv = c_int*128
    img = RGBImage(pilimg.size[0],
                   pilimg.size[1],
                   rgbmatrix[0].ctypes.data_as(POINTER(c_ubyte)),
                   rgbmatrix[1].ctypes.data_as(POINTER(c_ubyte)),
                   rgbmatrix[2].ctypes.data_as(POINTER(c_ubyte)))
    ret = libccv.calc_ccv(pointer(img),threashold)
    descriptor = np.ctypeslib.as_array(ccv.from_address(ret))
    descriptor = descriptor.copy()
    libccv.delete_ptr(ret)
    return descriptor


def reduce_color(pilimg,size):
    pilimg = pilimg.convert(mode='RGB')
    pilimg.thumbnail((size, size), Image.ANTIALIAS)
    rgbmatrix = __preprocess_scipy(pilimg)
    img = RGBImage(pilimg.size[0],
                   pilimg.size[1],
                   rgbmatrix[0].ctypes.data_as(POINTER(c_ubyte)),
                   rgbmatrix[1].ctypes.data_as(POINTER(c_ubyte)),
                   rgbmatrix[2].ctypes.data_as(POINTER(c_ubyte)))
    libccv.destructive_reduce_colors(pointer(img))
    return to_pil(rgbmatrix.transpose(1, 2, 0))
