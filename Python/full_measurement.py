#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Generate full .rtdc test measurement"""
from __future__ import division, print_function, unicode_literals

import numpy as np

from rtdc_writer import write


path = "full_measurement.rtdc"
event_count = 10000
image_shape = (50, 90)
frame_count = event_count*100
frames = np.sort(np.random.choice(frame_count, event_count, replace=False))


meta_data = {
    # All parameters related to the actual experiment
    "experiment": {
        "date": "2017-11-11",
        "event count": event_count,
        "run index": 1,
        "sample": "artificial test data",
        "time": "11:11:11",
        },
    # All special keywords related to RT-FDC
    "fluorescence": {
        "bit depth": 16,
        "channel count": 3,
        "laser 1 power": 100,
        "laser 2 power": 200,
        "laser 3 power": 300,
        "laser 1 lambda": 488,
        "laser 2 lambda": 561,
        "laser 3 lambda": 640,
        "sample rate": 500000,
        "signal max": 1,
        "signal min": -1,
        "trace median": 20,
        },
    # All imaging-related keywords
    "imaging": {
        "exposure time": 20,
        "flash current": 100,
        "flash device": "green LED)",
        "flash duration": 10,
        "frame rate": 2000,
        "pixel size": 0.34,
        "roi position x": 234,
        "roi position y": 135,
        "roi size x": image_shape[0],
        "roi size y": image_shape[1],
        },
    # All setup-related keywords, except imaging
    "setup": {
        "channel width": 30,
        "chip region": "channel",
        "flow rate": .16,
        "flow rate sample": .10,
        "flow rate sheath": .6,
        "medium": "CellCarrierB",
        "module composition": "AcCellerator,HeatModule",
        "software version": "in-silico 0.0.1",
        "temperature": 22.5,
        },
    }



data = {"area_cvx": np.random.normal(100, 5, event_count),
        "area_msd": np.random.normal(100, 5, event_count) - np.abs(np.random.normal(10, 3, event_count)),
        "circ": 1 - np.abs(np.random.normal(0, .2, event_count)),
        "fl1_area": np.random.normal(300, 100, event_count),
        "fl1_dist": np.zeros(event_count),
        "fl1_max": np.random.normal(1000, 5, event_count),
        "fl1_npeaks": np.ones(event_count),
        "fl1_pos": 300 * np.ones(event_count),
        "fl1_width": np.random.normal(400, 10, event_count),
        "fl2_max": np.random.normal(2000, 10, event_count),
        "fl3_max": np.random.normal(1600, 15, event_count),
        "frame": frames,
        "ncells": np.ones(event_count),
        "pos_x": np.linspace(image_shape[0]/2 - 10, image_shape[0]/2 + 4, event_count),
        "pos_y": np.linspace(image_shape[0]/2 + 2, image_shape[0]/2 -7, event_count),
        "size_x": np.linspace(22, 21, event_count),
        "size_y": np.linspace(21, 35, event_count),        
        }

# contour data
contx = np.concatenate((np.arange(20),
                        20*np.ones(20),
                        np.arange(20)[::-1],
                        np.zeros(20)))
conty = np.concatenate((20*np.ones(20),
                        np.arange(20)[::-1],
                        np.zeros(20),
                        np.arange(20)))

data["contour"] = []
for ii in range(event_count):
    conti = np.zeros((80, 2), dtype=int)
    x = data["pos_x"][ii]
    y = data["pos_y"][ii]
    conti[:, 0] = int(x) + contx.astype(int)
    conti[:, 1] = int(y) + conty.astype(int)
    data["contour"].append(conti)

# image data
images = np.ones((event_count, image_shape[0], image_shape[1]), dtype=np.uint8)
for ii in range(event_count):
    images[ii] += np.random.randint(0, 250, image_shape, dtype=np.uint8)
data["image"] = images


# trace data
xraw = np.linspace(-1, 1, 100)
med = np.exp(-xraw**2*1e3)
rawtrace = np.zeros((event_count, med.size))
medtrace = np.zeros((event_count, med.size))
for ii in range(event_count):
    med = np.roll(med, 7)
    raw = med + np.random.normal(scale=.1, size=100)
    medtrace[ii] = med
    rawtrace[ii] = raw
data["trace"] = {"fl1_median": medtrace,
                 "fl1_raw": rawtrace,
                 }

write(rtdc_file=path, data=data, meta=meta_data, compression=None)
