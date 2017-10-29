#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT DC file format writer"""
from __future__ import unicode_literals

import os
import time

import dclab
import h5py
import numpy as np


def store_contour(h5group, data):
    if not isinstance(data, (list, tuple)):
        # single event
        data = [data]
    if "contour" not in h5group:
        dset = h5group.create_group("contour")
        for ii, cc in enumerate(data):
            dset.create_dataset("{}".format(ii), data=cc)    
    else:
        grp = h5group["contour"]
        curid = len(grp["contour"].keys())
        for ii, cc in enumerate(data):
            grp.create_dataset("{}".format(curid + ii), data=cc)        


def store_image(h5group, data):
    if len(data.shape) == 2:
        # single event
        data = data.reshape(1, data.shape[0], data.shape[1])
    if "image" not in h5group:
        maxshape = (None, data.shape[1], data.shape[2])
        chunks = (1, data.shape[1], data.shape[2])
        dset = h5group.create_dataset("image",
                                      data=data,
                                      maxshape=maxshape,
                                      chunks=chunks)
        # Create and Set image attributes
        # HDFView recognizes this as a series of images
        dset.attrs["CLASS"] = "IMAGE"
        dset.attrs["IMAGE_VERSION"] = "1.2"
        dset.attrs["IMAGE_SUBCLASS"] = "IMAGE_GRAYSCALE"
    else:
        dset = h5group["image"]
        oldsize = dset.shape[0]
        dset.resize(oldsize + data.shape[0], axis=0)
        dset[oldsize:] = data


def store_scalar(h5group, name, data):
    if np.isscalar(data):
        # single event
        data = np.atleast_1d(data)
    if name not in h5group:
        h5group.create_dataset(name,
                               data=data,
                               maxshape=(None,),
                               chunks=True)        
    else:
        dset = h5group[name]
        oldsize = dset.shape[0]
        dset.resize(oldsize + data.shape[0], axis=0)
        dset[oldsize:] = data


def store_trace(h5group, data):
    if len(data.values()[0].shape) == 1:
        # single event
        for dd in data:
            data[dd] = data[dd].reshape(1, -1)    
    if "trace" not in h5group:
        grp = h5group.create_group("trace")
        for flt in data:
            maxshape = (None, data[flt].shape[-1])
            grp.create_dataset(flt,
                               data=data[flt],
                               maxshape=maxshape,
                               chunks=True)
    else:
        grp = h5group["trace"]
        for flt in data:
            dset = grp[flt]
            oldsize = dset.shape[0]
            dset.resize(oldsize + data[flt].shape[0], axis=0)
            dset[oldsize:] = data[flt]        
    

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
        must be given according to the feature type:
        
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
        feat_keys = data.features()
        newmeta = {}
        for mk in dclab.dfn.CFG_METADATA:
            newmeta[mk] = dict(data.config[mk])
        newmeta.update(meta)
        meta = newmeta
    elif isinstance(data, dict):
        # dictionary
        feat_keys = list(data.keys())
        feat_keys.sort()
    else:
        msg = "`data` must be dict or RTDCBase"
        raise ValueError(msg)

    ## Write meta data
    for sec in meta:
        if sec not in dclab.dfn.CFG_METADATA:
            # only allow writing of meta data that are not editable
            # by the user (not dclab.dfn.CFG_ANALYSIS)
            msg = "Meta data section not defined in dclab: {}".format(sec)
            raise ValueError(msg)
        for ck in meta[sec]:
            idk = "{}:{}".format(sec, ck)
            if ck not in dclab.dfn.config_keys[sec]:
                msg = "Meta data key not defined in dclab: {}".format(idk)
                raise ValueError(msg)
            conftype = dclab.dfn.config_types[sec][ck]
            rtdc_file.attrs[idk] = conftype(meta[sec][ck])

    ## Write data
    # data sanity checks
    for kk in feat_keys:
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
    for fk in feat_keys:
        if fk in dclab.dfn.feature_names:
            store_scalar(h5group=events,
                         name=fk,
                         data=data[fk])
        elif fk == "contour":
            store_contour(h5group=events,
                          data=data["contour"])
        elif fk == "image":
            store_image(h5group=events,
                        data=data["image"])
        elif fk == "trace":
            store_trace(h5group=events,
                        data=data["trace"])


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


def test_meta():
    data = {"area_um": np.linspace(100.7, 110.9, 1000)}
    rtdc_file = "test_meta.rtdc"
    if os.path.exists(rtdc_file):
        os.remove(rtdc_file)
    meta = {"setup": {
                "channel width": 20,
                "chip region": "Channel",
                },
            "online_contour": {
                "no absdiff": "True",
                "image blur": 3.0,
                },
            }
    write(rtdc_file, data, meta=meta)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    assert rtdc_data.attrs["online_contour:no absdiff"] == True
    assert isinstance(rtdc_data.attrs["online_contour:image blur"], int)
    assert rtdc_data.attrs["setup:channel width"] == 20
    assert rtdc_data.attrs["setup:chip region"] == "channel"
    

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
