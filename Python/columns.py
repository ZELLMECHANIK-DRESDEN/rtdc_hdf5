# These are columns that contain a scalar value for each event.
# Other valid columns are "image", "contour", and "trace".
_columns = [
   ["area_cvx", "Convex area [px]"],
   ["area_msd", "Measured area [px]"],
   ["area_ratio", "Convex to measured area ratio"],
   # area_um is the convex area per definition
   ["area_um", "Area [µm²]"],
   ["aspect", "Aspect ratio of bounding box"],
   ["bright_avg", "Brightness average within contour [a.u.]"],
   ["bright_sd", "Brightness SD  within contour [a.u.]"],
   ["circ", "Circularity"],
   ["deform", "Deformation"],
   ["emodulus", "Young's Modulus [kPa]"],
   # fl*_area, fl*_pos, and fl*_width values correspond to the
   # object for which the contour was found. For high concentrations,
   # these values could be error-prone due to the assignment from
   # false objects. 
   ["fl1_area", "FL-1 area of peak [a.u.]"],
   # fl1_dist is set to zero if there is only one peak
   ["fl1_dist", "FL-1 distance between two first peaks [µs]"],
   ["fl1_max", "FL-1 maximum [a.u.]"],
   ["fl1_npeaks", "FL-1 number of peaks"],
   ["fl1_pos", "FL-1 position of peak [µs]"],
   ["fl1_width", "FL-1 width [µs]"],
   ["fl2_area", "FL-2 area of peak [a.u.]"],
   ["fl2_dist", "FL-2 distance between two first peaks [µs]"],
   ["fl2_max", "FL-2 maximum [a.u.]"],
   ["fl2_npeaks", "FL-2 number of peaks"],
   ["fl2_pos", "FL-2 position of peak [µs]"],
   ["fl2_width", "FL-2 width [µs]"],
   ["fl3_area", "FL-3 area of peak [a.u.]"],
   ["fl3_dist", "FL-3 distance between two first peaks [µs]"],
   ["fl3_max", "FL-3 maximum [a.u.]"],
   ["fl3_npeaks", "FL-3 number of peaks"],
   ["fl3_pos", "FL-3 position of peak [µs]"],
   ["fl3_width", "FL-3 width [µs]"],
   ["frame", "Video frame number"],
   # The inertia ratios of the event contours are defined by the
   # central second order moments of area. 
   ["inert_ratio_cvx", "Inertia ratio of convex contour sqrt(m20/m02)"],
   ["inert_ratio_raw", "Inertia ratio of raw contour sqrt(m20/m02)"],
   ["index", "Event index"],
   ["ncells", "Number of cells in image"],
   ["pc1", "Principal component 1"],
   ["pc2", "Principal component 2"],
   ["pos_x", "Position along channel axis [µm]"],
   ["pos_y", "Position lateral in channel [µm]"],
   ["size_x", "Bounding box size x [µm]"],
   ["size_y", "Bounding box size y [µm]"],
   ["time", "Event time [s]"],
   ["volume", "Volume [µm³]"],
   ]
