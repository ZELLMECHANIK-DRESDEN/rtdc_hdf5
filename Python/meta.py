#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# A list of all valid configuration keywords for a measurement.
# The variable names depict the corresponding section title in
# a configuration file, e.g.
#
#    [setup]
#    channel width = 20
#    chip region = channel
#    ...
#    [imaging]
#    exposure time = 20
#    ...
#    etc.


meta = {
    # All parameters related to the actual experiment
    "experiment": [
        # no correspondence
        ["date", str, "Date of measurement ('YYYY-MM-DD')"],
        # no correspondence
        ["event count", int, "Number of recorded events"],
        # General - Measurement Number
        ["run index", int, "Index of measurement run"],
        # no correspondence
        ["sample", str, "Measured sample or user-defined reference"],
        # no correspondence
        ["time", str, "Start time of measurement ('HH:MM:SS')"],
        ],
    # All special keywords related to RT-FDC
    "fluorescence": [
        # FLUOR - Bitdepthraw = 16
        ["bit depth", int, "Trace bit depth"],
        # FLUOR - FL-Channels = 1
        ["channel count", int, "Number of channels"],
        # FLUOR - Laser Power 488 [mW] = 0
        ["laser 1 power", float, "Laser 1 output power [mW]"],
        # FLUOR - Laser Power 561 [mW] = 0
        ["laser 2 power", float, "Laser 2 output power [mW]"],
        # FLUOR - Laser Power 640 [mW] = 0
        ["laser 3 power", float, "Laser 3 output power [mW]"],
        # no correspondence
        ["laser 1 lambda", float, "Laser 1 wavelength [nm]"],
        # no correspondence
        ["laser 2 lambda", float, "Laser 2 wavelength [nm]"],
        # no correspondence
        ["laser 3 lambda", float, "Laser 3 wavelength [nm]"],
        # FLUOR - Samplerate = 1000000
        ["sample rate", float, "Trace sample rate [Hz]"],
        # FLUOR - ADCmax = 1
        ["signal max", float, "Upper voltage detection limit [V]"],
        # FLUOR - ADCmin = -1
        ["signal min", float, "Lower voltage detection limit [V]"],
        # no correspondence
        ["trace median", int, "Rolling median filter size for traces"],
        ],
    # All tdms-related parameters
    "fmt_tdms": [
        ["video frame offset", int, "Missing events at beginning of video"],
        ],
    # All imaging-related keywords
    "imaging": [
        # Framerate - Shutter Time
        ["exposure time", float, "Sensor exposure time [µs]"],
        # General - Current LED [A]
        ["flash current", float, "Light source current [A]"],
        # no correspondence
        ["flash device", str, "Light source device type (e.g. green LED)"],
        # General -  Shutter Time LED [us]
        ["flash duration", float, "Light source flash duration [µs]"],
        # Framerate - Frame Rate
        ["frame rate", float, "Imaging frame rate [Hz]"],
        # Image - Pix Size
        ["pixel size", float, "Pixel size [µm]"],
        # ROI - x-pos
        ["roi position x", float, "Image x coordinate on sensor [px]"],
        # ROI - y-pos
        ["roi position y", float, "Image y coordinate on sensor [px]"],
        # ROI - width
        ["roi size x", int, "Image width [px]"],
        # ROI - height
        ["roi size y", int, "Image height [px]"],
        ],
    # All parameters for online contour extraction from the event images
    "online_contour": [
        # Image - Trig Thresh = 50
        ["bin area min", int, "Minium pixel area of binary image event"],
        # Image - Bin Ops = 5
        ["bin kernel", int, "Odd ellipse kernel size, binary image morphing"],
        # Image - Margin = 0
        ["bin margin", int, "Remove margin in x for contour detection"],
        # Image - Thresh = 6
        ["bin threshold", int, "Binary threshold for avg-bg-corrected image"],
        # Image - Blur = 0
        ["image blur", int, "Odd sigma for Gaussian blur (21x21 kernel)"],
        # Image - Diff_Method = 1
        ["no absdiff", bool, "Avoid OpenCV 'absdiff' for avg-bg-correction"],
        ],
    # All online filters
    "online_filter": [
        # Image - Cell Aspect Min
        ["aspect min", float, "Minimum aspect ratio of bounding box"],
        # Image - Cell Aspect Max
        ["aspect max", float, "Maximum aspect ratio of bounding box"],
        # Image - Cell Max Length = 80.000000
        ["size_x max", int, "Maximum bounding box size x [µm]"],
        # Image - Cell Max Height = 20.000000
        ["size_y max", int, "Maximum bounding box size y [µm]"],
        # no correspondence
        ["size_x min", int, "Minimum bounding box size x [µm]"],
        # no correspondence
        ["size_y min", int, "Minimum bounding box size y [µm]"],
        ],
    # All setup-related keywords, except imaging
    "setup": [
        # General - Channel width
        ["channel width", float, "Width of microfluidic channel [µm]"],
        # General - Region
        ["chip region", str, "Imaged chip region (channel or reservoir)"],
        # General - Flow Rate [ul/s]
        ["flow rate", float, "Flow rate in channel [µL/s]"],
        # General - Sample Flow Rate [ul/s]
        ["flow rate sample", float, "Sample flow rate [µL/s]"],
        # General - Sheath Flow Rate [ul/s]
        ["flow rate sheath", float, "Sheath flow rate [µL/s]"],
        # no correspondence
        ["medium", str, "The medium used (e.g. CellCarrierB, water)"],
        # Image - Setup
        ["module composition", str, "Comma-separated list of modules used"],
        # no correspondence
        ["software version", str, "Acquisition software with version"],
        # FLUOR - Ambient Temperature
        ["temperature", float, "Chip temperature [°C]"],
        # no correspondence
        ["viscosity", float, "Medium viscosity [Pa*s], if 'medium' not given"]
        ],
    }
