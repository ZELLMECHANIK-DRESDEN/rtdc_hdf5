Python implementation of the .rtdc file format

This directory contains the following files:

- `features.py`: A list of all valid scalar features names (non-scalars are `image`, `contour`, and `trace`), see #5
- `meta.py`: A list of all valid configuration keywords (variable names are section headings)
- `rtdc_writer_proof.py`: A proof-of-principle writer for the .rtdc file format, see #2, #4, #5
