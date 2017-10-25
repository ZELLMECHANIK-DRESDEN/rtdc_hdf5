#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT DC file format writer"""
from __future__ import unicode_literals

import os
import time

import dclab
import h5py
import numpy as np

import columns
import meta


def write(rtdc_file, data, meta={}, close=True):
    """Write data to an RT-DC file
    
    Parameters
    ----------
    rtdc_file: path or h5py.File
        The file to write to. If it is a path, an instance of
        `h5py.File` will be created. If it is an instance of
        `h5py.File`, the data will be appended.
    data: dict or dclab.rtdc_dataset.RTDCBase
        The data to store. Each key of `data` must either be a valid
        scalar feature name (see `dclab.dfn.FEATURES`) or
        one of ["contour", "image", "trace"]. The data type
        must be given according to the column type:
        
        - scalar feature: 1d ndarray of size `N`, any dtype,
          with the number of events `N`.
        - contour: list of `N` 2d ndarrays of shape `(2,C)`, any dtype,
          with each ndarray containing the x- and y- coordinates
          of `C` contour points in pixels.
        - image: 3d ndarray of shape `(N,A,B)`, uint8,
          with the image dimensions `(x,y) = (A,B)`
        - trace: 2d ndarray of shape `(N,T)`, any dtype
          with a globally constant trace length `T`.
    meta: dict of dicts
        The meta data to store (see `dclab.dfn.CFG_METADATA`).
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
    
    if isinstance(data, dclab.rtdc_dataset.RTDCBase):
        # RT-DC data set
        keys = data.features()
    elif isinstance(data, dict):
        # dictionary
        keys = list(data.keys())
        keys.sort()
    else:
        msg = "`data` must be dict or RTDCBase"
        raise ValueError(msg)
    # sanity checks
    for kk in keys:
        if not (kk in dclab.dfn.feature_names or
                kk in ["contour", "image", "trace"]):
            msg = "Unknown data key: {}".format(kk)
            raise ValueError(msg)
        if kk == "trace":
            for sk in data["trace"]:
                if sk not in dclab.dfn.FLUOR_TRACES:
                    msg = "Unknown trace key: {}".format(sk)
                    raise ValueError(msg)   
    # create events group
    if "events" not in rtdc_file:
        rtdc_file.create_group("events")
    events = rtdc_file["events"]
    # determine if we have a single event
    for kk in keys:
        if kk in dclab.dfn.feature_names:
            if np.isscalar(data[kk]):
                single = True
            else:
                single = False
            break
    else:
        msg = "`data` must contain scalar feature data"
        raise NotImplementedError(msg)
    
    for key in keys:
        dat = data[key]
        # convert single events
        if single:
            if key in dclab.dfn.feature_names:
                # scalar to array
                dat = np.atleast_1d(dat)
            elif key == "contour":
                # array must be in list
                dat = [dat]
            elif key == "image":
                # image array has first axis as index of images
                dat = dat.reshape(1, dat.shape[-2], dat.shape[-1])
            elif key == "trace":
                # each trace data array has first axis as index
                for dd in dat:
                    dat[dd] = dat[dd].reshape(1, -1)
        # write data
        if key not in events:
            # initialize groups and datasets
            if key in dclab.dfn.feature_names:
                events.create_dataset(key,
                                      data=dat,
                                      maxshape=(None,),
                                      chunks=True)
            elif key == "contour":
                events.create_group(key)
                dset = events["contour"]
                for ii, cc in enumerate(dat):
                    dset.create_dataset("{}".format(ii), data=cc)
            elif key == "image":
                maxshape = (None, dat.shape[1], dat.shape[2])
                chunks = (1, dat.shape[1], dat.shape[2])
                events.create_dataset(key,
                                      data=dat,
                                      maxshape=maxshape,
                                      chunks=chunks)
                # Create and Set image attributes
                # HDFView recognizes this as a series of images
                dset = events["image"]
                dset.attrs["CLASS"] = "IMAGE"
                dset.attrs["IMAGE_VERSION"] = "1.2"
                dset.attrs["IMAGE_SUBCLASS"] = "IMAGE_GRAYSCALE"
            elif key == "trace":
                events.create_group(key)
                for flt in dat:
                    maxshape = (None, dat[flt].shape[-1])
                    grp = events["trace"]
                    grp.create_dataset(flt,
                                       data=dat[flt],
                                       maxshape=maxshape,
                                       chunks=True)
        else:
            # append data
            if key in dclab.dfn.feature_names or key == "image":
                dset = events[key]
                oldsize = dset.shape[0]
                dset.resize(oldsize + dat.shape[0], axis=0)
                dset[oldsize:] = dat
            elif key == "contour":
                grp = events[key]
                curid = len(grp["contour"].keys())
                for ii, cc in enumerate(dat):
                    grp.create_dataset("{}".format(curid + ii), data=cc)
            elif key == "trace":
                grp = events[key]
                for flt in dat:
                    dset = grp[flt]
                    oldsize = dset.shape[0]
                    dset.resize(oldsize + dat[flt].shape[0], axis=0)
                    dset[oldsize:] = dat[flt]


def test_bulk_scalar():
    data = {"area_um": np.linspace(100.7, 110.9, 1000)}
    rtdc_file = "test_bulk_scalar.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "area_um" in events.keys()
    assert np.all(events["area_um"][:] == data["area_um"])


def test_bulk_contour():
    num = 20
    contour = []
    for ii in range(5, num + 5):
        cii = np.arange(2 * ii).reshape(2, ii)
        contour.append(cii)
    data = {"area_um": np.linspace(100.7, 110.9, num),
            "contour": contour}
    rtdc_file = "test_bulk_contour.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "contour" in events.keys()
    assert np.allclose(events["contour"]["10"], contour[10])


def test_bulk_image():
    num = 20
    image = np.arange(20 * 90 * 50).reshape(20, 90, 50)
    data = {"area_um": np.linspace(100.7, 110.9, num),
            "image": image}
    rtdc_file = "test_bulk_image.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "image" in events.keys()
    assert np.allclose(events["image"][10], image[10])


def test_bulk_trace():
    num = 20
    trace = {"fl1_median": np.arange(num * 333).reshape(num, 333),
             "fl1_raw": 13 + np.arange(num * 333).reshape(num, 333),
             }
    data = {"area_um": np.linspace(100.7, 110.9, num),
            "trace": trace}
    rtdc_file = "test_bulk_trace.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "trace" in events.keys()
    assert np.allclose(events["trace"]["fl1_raw"], trace["fl1_raw"])


def test_real_time():
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
            
            data = {"area_um": axis1,
                    "area_cvx": axis2,
                    "image": num_img}
            
            write(fobj,
                  data=data,
                  close=False
                  )

    print("Time to write {} events: {:.2f}s".format(N*M, time.time()-a))
    
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert events["image"].shape == (N, shy, shx)
    assert events["area_um"].shape == (N,)
    assert np.dtype(events["area_um"]) == np.float
    assert np.dtype(events["area_cvx"]) == np.int


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
