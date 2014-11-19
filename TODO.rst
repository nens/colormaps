todo
====

base tasks
----------

The tasks of any colormap should be:

- loading from a json file or string (over the web)
- Making masked values transparent (or arbitrary color?): ma.masked_outside

discrete tasks
--------------
Outside the domain, it is no_data. (transparent, or arbitrary color)
data => mask everything outside domain => lut, done.

__init__: values, colors, outside=(0, 0, 0, 0)
__call__: data

scalar tasks
------------
prescale stops and data using linear, logarithmic or interpolation scaling
Any colormap is internally mapped to the 0,1 domain.

When called, data is clipped to stops limits
Lookuptable.
The specified data limits indicate what data portion needs to match the domain
Outside the domain

No separate normalize, since it happens inside the call:

data => clip => scale to [0, 1] domain => 

What cases are covered in this way?

-classic matplotlib 0,1 colormaps, used with normalize/limits
-classic matplotlib 0,1 colormaps, used with custom normalizer
-vito colormap with logarithmic normalization and arbitrary stops
-discrete colormaps


__init__: values, colors, segments, outside=(0, 0, 0, 0), scale='linear')
    - initialize a scale function
    - put the values through that scale function
    - interpolate colors?

scaling can be 'linear', 'logarithmic', {'custom': 'path_to_scale'}
__call__(data, vmin=None, vmax=None, scale=None)

