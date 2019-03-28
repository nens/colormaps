Changelog of colormaps
===================================================


1.9 (unreleased)
----------------

- Nothing changed yet.


1.8 (2019-03-07)
----------------

- Solve an IndexError in some edge case in GradientColorMap.


1.7 (2019-01-16)
----------------

- Removed np.round() in gradient CM index calculation.


1.6 (2019-01-14)
----------------

- Performing additional masking in Data.convert()


1.5 (2018-03-08)
----------------

- Colormaps accept raster-store-like data dictionaries for better performance

- Mappings using the `interp` argument can handle unsorted values

- `interp` can handle mappings that change the sign (negate)

- The order of interp and log is swapped: first interp, then log


1.4.1 (2017-11-02)
------------------

- Fixed legend bug.


1.4 (2017-10-03)
----------------

- Cast integer interpolations to floats to fix test

- Be clearer about the in-place log() on the interpolation inputs

- Add function to give a range of numbers to use in legends


1.3 (2016-06-14)
----------------

- Add colormaps and labels for forests, deforestation and floods.

- Remove the white haze in radar images.

- Add Port Elisabeth SA soil and land-cover colormaps.

- Change drought to non-free colormap.

- Update labels and colors of indonesia flood map.

- Coerce to dicts for embedded labels in colormap definitions.

- Update MANIFEST file.


1.2.4 (2015-01-27)
------------------

- Add vietnam cover colors.


1.2.3 (2015-01-19)
------------------

- Add the missing 5min variant for radar.


1.2.2 (2015-01-15)
------------------

- Adjust base colormap for radar, differentiate as well.


1.2.1 (2014-12-23)
------------------

- Labeling is vectorized now.

- Add world soil colors and labels.


1.2 (2014-12-17)
----------------

- Add label functionality by locale


1.1.1 (2014-12-15)
------------------

- Rearrange some colors.


1.1 (2014-12-08)
----------------

- Really use masked for discrete when outside limits

- Add manager

- Add colormaps


1.0 (2014-11-25)
----------------

- Handle masked arrays

- Init from a config

- Do (log) normalization and interpolation

- Handle limits for both types of maps

- Custom values for invalid (only discrete) and masked

- Add cdict converter


0.1.2 (2014-05-22)
------------------

- Simplify access to registered colormaps


0.1.1 (2014-05-22)
------------------

- Any gradient stops are now allowed.


0.1 (2014-04-16)
----------------

- Initial project structure created with nensskel 1.34.dev0.

- Implemented gradients and discrete colormaps.
