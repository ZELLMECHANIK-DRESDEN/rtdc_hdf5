#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT DC file format writer"""
from __future__ import unicode_literals

import os
import time

import h5py
import numpy as np

import columns
import meta


def write(rtdc_file, name, data, meta={}, close=True):
    """Write data to RT-DC file
    
    Parameters
    ----------
    rtdc_file: path or h5py.File
        The file to write to. If it is a path, an instance of
        `h5py.File` will be created. If it is an instance of
        `h5py.File`, the data will be appended.
    data: dict
        The data to store. Each key of `data` must either be a valid
        scalar column name (see `dclab.definitions`) or
        one of ["contour", "image", "trace"]. The data type
        must be given according to the column type:
        
        - scalar columns: 1d ndarray of size `N`, any dtype,
          with the number of events `N`.
        - contour: list of `N` 2d ndarrays of shape `(2,C)`, any dtype,
          with each ndarray containing the x- and y- coordinates
          of `C` contour points in pixels.
        - image: 3d ndarray of shape `(N,A,B)`, uint8,
          with the image dimensions `(x,y) = (A,B)`
        - trace: 2d ndarray of shape `(N,T)`, any dtype
          with a globally constant trace length `T`.
    meta: dict of dicts
        The meta data to store (see `dclab.definitions`).
        Each key depicts a meta data section name whose data is given
        as a dictionary, e.g.
        
            meta = {"imaging": {"exposure time": 20,
                                "flash duration": 2,
                                ...
                                },
                    "setup": {"channel width": 20,
                              "chip region": "channel",
                              ...
                              },
                    ...
                    }
        
        Only section key names and key values therein registered
        in dclab are allowed and are converted to the pre-defined
        dtype.
    close: bool
        When set to `True` (default), the `h5py.File` object will
        be closed and `None` is returned. When set to `False`,
        the `h5py.File` object will be returned (useful for
        real-time data acquisition).
    """
    if not isinstance(rtdc_file, h5py.File):
        rtdc_file = h5py.File(rtdc_file, "w")
    
    if not isinstance(name, (list,tuple)):
        name = [name]
        data = [data]

    if "events" not in rtdc_file:
        rtdc_file.create_group("events")
    
    events = rtdc_file["events"]
    
    for nam, dat in zip(name, data):
        if np.isscalar(dat):
            dat = np.atleast_1d(dat)
        elif nam == "image":
            if len(dat.shape) != 3:
                dat = dat.reshape(1, dat.shape[0], dat.shape[1])

        if nam not in events:
            # Initialize the dataset
            if len(dat.shape) == 1:
                maxshape = (None,)
                chunks = True
            else:
                # images
                maxshape = (None, dat.shape[1], dat.shape[2])
                chunks = (1, dat.shape[1], dat.shape[2])
            events.create_dataset(nam,
                                  data = dat,
                                  maxshape=maxshape,
                                  chunks=chunks)
            if nam=="image":
                dset = events[nam]
                # add attributes for images to be detected properly
                # from https://github.com/h5py/h5py/issues/771
                # Create and Set image attributes
                # hdfView recognizes this a series of images
                dset.attrs.create(b'CLASS', b'IMAGE')
                dset.attrs.create(b'IMAGE_VERSION', b'1.2')
                dset.attrs.create(b'IMAGE_SUBCLASS', b'IMAGE_GRAYSCALE')
                #dset.attrs.create('IMAGE_MINMAXRANGE', np.array([0,255], dtype=np.uint8))
        else:
            # Add new data
            dset = events[nam]
            oldsize = dset.shape[0]
            dset.resize(oldsize+dat.shape[0], axis=0)
            dset[oldsize:] = dat


def test_bulk_write():
    data = np.linspace(100.7, 110.9, 1000)
    name = "area"
    rtdc_file = "test_bulk.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    write(rtdc_file, name, data)
    
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert name in events.keys()
    assert np.all(events[name][:] == data)


def test_real_time_write():
    import cv2

    # Create huge array
    N = 11440
    # Writing 10 images at a time is faster than writing one image at a time
    M = 10
    assert N//M == np.round(N/M)
    shx = 256
    shy = 96
    images = np.zeros((M, shy, shx), dtype=np.uint8)
    axis1 = np.linspace(0,1,M)
    axis2 = np.arange(M)
    rtdc_file = "test_rt.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    
    a = time.time()
    
    with h5py.File(rtdc_file, "a") as fobj:
        # simulate real time and write one image at a time
        for _ii in range(N//M):
            #print(ii)
            num_img = np.copy(images)
            for _iii in range(len(images)):
                # put pos in chunk and nr of chunk into images
                cv2.putText(num_img[_iii], str(_iii)+" chunk:"+str(_ii)
                            ,(20,50), cv2.FONT_HERSHEY_PLAIN, 1.0, 255)
                cv2.putText(num_img[_iii], str(_iii+M*_ii)
                            ,(20,70), cv2.FONT_HERSHEY_PLAIN, 1.0, 50)
            

            write(fobj,
                  name=["image", "axis1", "axis2"],
                  data=[num_img[:], axis1[:], axis2[:]],
                  close=False
                  )

    print("Time to write {} events: {:.2f}s".format(N*M, time.time()-a))
    
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert events["image"].shape == (N, shy, shx)
    assert events["axis1"].shape == (N,)
    assert np.dtype(events["axis1"]) == np.float
    assert np.dtype(events["axis2"]) == np.int


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
    
    
