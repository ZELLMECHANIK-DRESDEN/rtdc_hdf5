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


# All setup-related keywords, except imaging
setup = [
    # General - Channel width
    ["channel width", "Width of microfluidic channel [µm]"],
    # General - Region
    ["chip region", "Imaged chip region (channel or reservoir)"],
    # General - Flow Rate [ul/s]
    ["flow rate", "Flow rate in channel [µl/s]"],
    # General - Sample Flow Rate [ul/s]
    ["flow rate sample", "Sample flow rate [µl/s]"],
    # General - Sheath Flow Rate [ul/s]
    ["flow rate sheath", "Sheath flow rate [µl/s]"],
    # no correspondence
    ["medium", "The medium used (e.g. CellCarrier, CellCarrierB, water)"],
    # Image - Setup
    ["module composition", "Comma-separated list of modules used"],
    # no correspondence
    ["software version", "Acquisition software with version"],
    # FLUOR - Ambient Temperature
    ["temperature", "Chip temperature [°C]"],
    ]

# All imaging-related keywords
imaging = [
    # Framerate - Shutter Time
    ["exposure time", "Sensor exposure time [µs]"],
    # no correspondence
    ["flash device", "Light source device type (e.g. green LED)"],
    # General -  Shutter Time LED [us]
    ["flash duration", "Light source flash duration [µs]"],
    # Framerate - Frame Rate
    ["frame rate", "Imaging frame rate [Hz]"],
    # Image - Pix Size
    ["pixel size", "Pixel size [µm]"],
    # ROI - x-pos
    ["roi position x", "Image x coordinate on sensor [px]"],
    # ROI - y-pos
    ["roi position y", "Image y coordinate on sensor [px]"],
    # ROI - width
    ["roi size x", "Image width [px]"],
    # ROI - height
    ["roi size y", "Image height [px]"],
    # Framerate - Tap Code
    ["tap code", "Camera data transfer tap code"], # What is this?
    # Framerate - Tap Mode
    ["tap mode", "Camera data transfer tap mode"], # What is this?
    ]

# All special keywords related to RT-FDC
fluorescence = [
    # FLUOR - Bitdepthraw = 16
    ["bit depth", "Trace bit depth"],
    # FLUOR - FL-Channels = 1
    ["channel count", "Number of channels"],
    # FLUOR - Laser Power 488 [mW] = 0
    ["laser 1 power", "Laser 1 output power [mW]"],
    # FLUOR - Laser Power 561 [mW] = 0
    ["laser 2 power", "Laser 2 output power [mW]"],
    # FLUOR - Laser Power 640 [mW] = 0
    ["laser 3 power", "Laser 3 output power [mW]"],
    # no correspondence
    ["laser 1 lambda", "Laser 1 wavelength [nm]"],
    # no correspondence
    ["laser 2 lambda", "Laser 2 wavelength [nm]"],
    # no correspondence
    ["laser 3 lambda", "Laser 3 wavelength [nm]"],
    # FLUOR - Samplerate = 1000000
    ["sample rate", "Trace sample rate"],
    ]

# All online filters
online_filter = [
    # Image - Cell Aspect Min
    ["aspect min", "Minimum aspect ratio of bounding box"],
    # Image - Cell Aspect Max
    ["aspect max", "Maximum aspect ratio of bounding box"],
    # Image - Cell Max Length = 80.000000
    ["size_px_x max", "Maximum bounding box size x [px]"],
    # Image - Cell Max Height = 20.000000
    ["size_py_y max", "Maximum bounding box size y [px]"],
    # no correspondence
    ["size_px_x min", "Minimum bounding box size x [px]"],
    # no correspondence
    ["size_py_y min", "Minimum bounding box size y [px]"],
    ]

# All parameters for online contour extraction from the event images
online_contour = [
    # Image - Bin Ops = 5
    ["bin kernel", "Ellipse morphing structure size of binary image (odd)"],
    # Image - Blur = 0
    ["image blur", "Sigma of Gaussian blur with 21x21 kernel size (odd)"],
    # Image - Diff_Method = 1
    ["no absdiff", "Avoid OpenCV`s 'absdiff' for bg-correction with average"],
    # Image - Thresh = 6
    ["threshold", "Threshold for binary image from bg-corrected image"],
    # Image - Trig Thresh = 50
    ["bin count min", "Minium pixel area of binary image event for contour"],
    # Image - Margin = 0
    ["bin count margin", "Remove margin in x for contour detection"],
    ]

# All parameters related to the actual experiment
experiment = [
    # no correspondence
    ["date", "Date of measurement (YYYY-MM-DD)"],
    # General - Measurement Number
    ["run count", "Index of measurement run"],
    # no correspondence
    ["sample", "Measured sample or user-defined reference"],
    # no correspondence
    ["time", "Start time of measurement (HH:MM:SS)"],
    ]


# These are configuration keywords that are deprecated,
# redundant, or do not contain any important information:
# FLUOR - Format = int16
# Image - Cell Min = 10.000000
# Image - Cell Max = 50

# These are configuration keywords that need an explanation: 
# Image - t1 = -256
# Image - t2 = -6
# FLUOR - ADCmin = -1
# FLUOR - ADCmax = 1
# Framerate - Tap Code
# Framerate - Tap Mode
