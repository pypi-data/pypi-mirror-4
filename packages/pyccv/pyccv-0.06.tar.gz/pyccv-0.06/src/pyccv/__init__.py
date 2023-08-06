#-*- coding: utf-8 -*-
from ctypes import POINTER
from ctypes import pointer
from ctypes import Structure
from ctypes import c_ubyte
from ctypes import c_int
from ctypes import c_void_p

import numpy as np
import os
import cv
import Image

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



def __preprocess(img):
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

def calc_ccv(pilimg,size,threashold):
    pilimg = pilimg.convert(mode='RGB')
    pilimg.thumbnail((size, size), Image.ANTIALIAS)
    rgbmatrix = __preprocess(pilimg)
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
