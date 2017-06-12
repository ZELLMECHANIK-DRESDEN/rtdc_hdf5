#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT DC file format writer"""
import os
import time

import h5py
import numpy as np

import cv2


def write_bulk(rtdc_file, name, data, chunks=None):
    """Write data to RT-DC file
    
    Parameters
    ----------
    rtdc_file: str or file object
        Path to file or file descriptor
    name: str or list of str
        Name of the column to save
    data: ndarray or list of ndarray
        The data to store
    """
    if not isinstance(name, (list,tuple)):
        name = [name]
        data = [data]
    

    if isinstance(rtdc_file, h5py.File):
        f = rtdc_file
        close = False
    else:
        f = h5py.File(rtdc_file, "a")
        close = True
    
    if "events" not in f:
        f.create_group("events")
    
    events = f["events"]
    
    for nam, dat in zip (name, data):
        events.create_dataset(nam, data=dat)

    if close:
        f.close()


def write_realtime(rtdc_file, name, data):
    """Write data to RT-DC file
    
    Parameters
    ----------
    rtdc_file: instance of `h5py.File` in write mode
        The file object to write to.
    name: str or list of str
        Name of the column to save
    data: ndarray or list of ndarray
        The data to store
    """
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
                dset.attrs.create('CLASS', 'IMAGE')
                dset.attrs.create('IMAGE_VERSION', '1.2')
                dset.attrs.create('IMAGE_SUBCLASS', 'IMAGE_GRAYSCALE')
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
    write_bulk(rtdc_file, name, data)
    
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert name in events.keys()
    assert np.all(events[name][:] == data)


def test_real_time_write():
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
            

            write_realtime(fobj,
                           name=["image", "axis1", "axis2"],
                           data=[num_img[:], axis1[:], axis2[:]]
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
    
    
