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

Considerations
--------------
Interpolation is nice, and is bypassed when limits are given. However,
the rgba lookup is then based on the interpolation. If limits are given,
should there be a final scale into the original values range, and then
proceed as if no limits were given?

What about a legend?
