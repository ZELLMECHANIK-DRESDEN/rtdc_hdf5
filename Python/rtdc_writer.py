#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT DC file format writer"""
from __future__ import unicode_literals

import os
import time
import sys

import dclab
import h5py
import numpy as np

if sys.version_info[0] == 2:
    h5str = unicode
else:
    h5str = str


def store_contour(h5group, data, compression="lzf"):
    if not isinstance(data, (list, tuple)):
        # single event
        data = [data]
    if "contour" not in h5group:
        dset = h5group.create_group("contour")
        for ii, cc in enumerate(data):
            dset.create_dataset("{}".format(ii),
                                data=cc,
                                fletcher32=True,
                                compression=compression)
    else:
        grp = h5group["contour"]
        curid = len(grp["contour"].keys())
        for ii, cc in enumerate(data):
            grp.create_dataset("{}".format(curid + ii),
                               data=cc,
                               fletcher32=True,
                               compression=compression)


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
                                      chunks=chunks,
                                      fletcher32=True,
                                      compression="szip")
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
                               chunks=True,
                               fletcher32=True)
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
                               chunks=True,
                               fletcher32=True)
    else:
        grp = h5group["trace"]
        for flt in data:
            dset = grp[flt]
            oldsize = dset.shape[0]
            dset.resize(oldsize + data[flt].shape[0], axis=0)
            dset[oldsize:] = data[flt]        
    

def write(rtdc_file, data={}, meta={}, logs={}, mode="reset",
          compression=None):
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
    logs: dict of lists
        Each key of `logs` refers to a list of strings that contains
        logging information. Each item in the list can be considered to
        be one line in the log file.
    mode: str
        Defines how the input `data` and `logs` are stored:
        - "append": append new data to existing Datasets; the opened
                    `h5py.File` object is returned (used in real-
                    time data storage)
        - "replace": replace keys given by `data` and `logs`; the
                    opened `h5py.File` object is closed and `None`
                    is returned (used for ancillary feature storage)
        - "reset": do not keep any previous data; the opened
                   `h5py.File` object is closed and `None` is returned
                   (default)
    compression: str
        Compression method for contour data and logs,
        one of ["lzf", "szip", "gzip"].
    """
    if mode not in ["append", "replace", "reset"]:
        raise ValueError("`mode` must be one of [append, replace, reset]")
    if not isinstance(rtdc_file, h5py.File):
        if mode == "reset":
            h5mode = "w"
        else:
            h5mode = "a"
        rtdc_file = h5py.File(rtdc_file, mode=h5mode)
    
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
    # remove previous data
    if mode == "replace":
        for rk in feat_keys:
            if rk in events:
                del events[rk]
    # store experimental data
    for fk in feat_keys:
        if fk in dclab.dfn.feature_names:
            store_scalar(h5group=events,
                         name=fk,
                         data=data[fk])
        elif fk == "contour":
            store_contour(h5group=events,
                          data=data["contour"],
                          compression=compression)
        elif fk == "image":
            store_image(h5group=events,
                        data=data["image"])
        elif fk == "trace":
            store_trace(h5group=events,
                        data=data["trace"])

    ## Write logs
    if "logs" not in rtdc_file:
        rtdc_file.create_group("logs")
    log_group = rtdc_file["logs"]
    # remove previous data
    if mode == "replace":
        for rl in logs:
            if rl in log_group:
                del log_group[rl]
    # store logs
    dt = h5py.special_dtype(vlen=h5str)
    for lkey in logs:
        ldata = logs[lkey]
        if isinstance(ldata, (str, h5str)):
            logs = [ldata]
        lnum = len(ldata)
        if lkey not in log_group:
            log_dset = log_group.create_dataset(lkey,
                                                (lnum,),
                                                dtype=dt,
                                                maxshape=(None,),
                                                chunks=True,
                                                fletcher32=True,
                                                compression=compression)
            for ii, line in enumerate(ldata):
                log_dset[ii] = line
        else:
            log_dset = log_group[lkey]
            oldsize = log_dset.shape[0]
            log_dset.resize(oldsize + lnum, axis=0)
            for ii, line in enumerate(ldata):
                log_dset[oldsize + ii] = line


def test_mode():
    data = {"area_um": np.linspace(100.7, 110.9, 1000)}
    data2 = {"deform": np.linspace(.7, .8, 1000)}
    
    rtdc_file = "test_replace.rtdc"
    write(rtdc_file, data=data, mode="reset")
    write(rtdc_file, data=data, mode="append")
    # Read the file:
    with h5py.File(rtdc_file) as rtdc_data1:
        events1 = rtdc_data1["events"]
        assert "area_um" in events1.keys()
        assert len(events1["area_um"]) == 2*len(data["area_um"])

    write(rtdc_file, data=data, mode="replace")
    write(rtdc_file, data=data2, mode="replace")
    with h5py.File(rtdc_file) as rtdc_data2:
        events2 = rtdc_data2["events"]
        assert "area_um" in events2.keys()
        assert "deform" in events2.keys()
        assert len(events2["area_um"]) == len(data["area_um"])


def test_bulk_scalar():
    data = {"area_um": np.linspace(100.7, 110.9, 1000)}
    rtdc_file = "test_bulk_scalar.rtdc"
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "area_um" in events.keys()
    assert np.all(events["area_um"][:] == data["area_um"])


def replace_contour():
    num = 20
    contour = []
    contour2 = []
    for ii in range(5, num + 5):
        cii = np.arange(2 * ii).reshape(2, ii)
        contour.append(cii)
        contour2.append(cii*2)
    
    data1 = {"area_um": np.linspace(100.7, 110.9, num),
             "contour": contour}
    data2 = {"contour": contour2}
    rtdc_file = "test_replace_contour.rtdc"
    write(rtdc_file, data1)
    write(rtdc_file, data2, mode="replace")
    # verify
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "contour" in events.keys()
    assert not np.allclose(events["contour"]["10"], contour[10])
    assert np.allclose(events["contour"]["10"], contour2[10])


def test_bulk_contour():
    num = 20
    contour = []
    for ii in range(5, num + 5):
        cii = np.arange(2 * ii).reshape(2, ii)
        contour.append(cii)
    data = {"area_um": np.linspace(100.7, 110.9, num),
            "contour": contour}
    rtdc_file = "test_bulk_contour.rtdc"
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
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "image" in events.keys()
    assert np.allclose(events["image"][10], image[10])


def test_bulk_logs():
    log = ["This is a test log that contains two lines.",
           "This is the second line.",
           ]
    rtdc_file = "test_bulk_logs.rtdc"
    write(rtdc_file, logs={"testlog": log})
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    outlog = rtdc_data["logs"]["testlog"]
    for ii in range(len(outlog)):
        assert outlog[ii] == log[ii]


def test_bulk_trace():
    num = 20
    trace = {"fl1_median": np.arange(num * 333).reshape(num, 333),
             "fl1_raw": 13 + np.arange(num * 333).reshape(num, 333),
             }
    data = {"area_um": np.linspace(100.7, 110.9, num),
            "trace": trace}
    rtdc_file = "test_bulk_trace.rtdc"
    write(rtdc_file, data)
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    events = rtdc_data["events"]
    assert "trace" in events.keys()
    assert np.allclose(events["trace"]["fl1_raw"], trace["fl1_raw"])


def test_meta():
    data = {"area_um": np.linspace(100.7, 110.9, 1000)}
    rtdc_file = "test_meta.rtdc"
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
    

def test_append_logs():
    log1 = ["This is a test log that contains two lines.",
            "This is the second line.",
            ]
    log2 = ["These are other logging events.",
            "They are appended to the log.",
            "And may have different lengths."
            ]
    rtdc_file = "test_append_logs.rtdc"
    with h5py.File(rtdc_file, "w") as fobj:
        write(fobj, logs={"testlog": log1}, mode="append")
        write(fobj, logs={"testlog": log2}, mode="append")
    # Read the file:
    rtdc_data = h5py.File(rtdc_file)
    outlog = rtdc_data["logs"]["testlog"]
    for ii in range(len(outlog)):
        assert outlog[ii] == (log1 + log2)[ii]


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
    
    a = time.time()
    
    with h5py.File(rtdc_file, "w") as fobj:
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
                  mode="append",
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
