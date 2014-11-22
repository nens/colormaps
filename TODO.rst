todo
====

json init in the raster-server
------------------------------

In the colormap json, this translates to:
    class: discrete,
    interp: 'ahn2',
    size: 1024,
    log: true,
    data [
        (0, (0, 0, 0, 0)),
        ...
    ]
and the converter json:
[
    (0, 0),
    (2, 1)
]

Roadmap
-------
So, now log and interpolation will both be applied when present. Not
sure why anyone would want that, though.

- Test with real colors
- Finish the cdic converter
- Investigate behavior of the log and interpolation things.
- Make workable jsons
- Make workable interps in a folder
