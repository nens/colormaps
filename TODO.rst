todo
====

json init in the raster-server
------------------------------

In the colormap json, this translates to:
    class: discrete
    items: [{value: 0, color: [0, 0, 0, 0]}]
    size: 1024
    log: true
    interp: 'ahn2'
and the converter json:
    [{value: 0, color: [0, 0, 0, 0]}]

Roadmap
-------
We must rewrite again. scale is either linear, log or
interpolation. Interpolation may be given from an arbitrary domain,
but it is rescaled to the 0, 1 domain. When the colormap designer makes
sure the entered values correspond to the original interpolation domain
AND make the colormap non-free, it will result in the desired behaviour.

What about a legend? - no problem, that will always just call the
colormap with the same arguments as the map does, so that the result
will be the same. This does not hold for calls without limits to free
colormaps of course.
