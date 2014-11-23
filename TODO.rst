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
Again, things must change. The log scaling must not do the * (e - 1) + 1.
The interpolation must always function, but when used with limits, it
must clip => interpolate => stretch. In this way the statistics of the data
are respected, but scaling stays possible.

Using only scale:
    scale to have limits at 0,1 (start with clip if limits)
    log and scale to have limits at 0,1 (start with clip if limits)
Using interp:
    interp to have limits at 0,1 (add pre-clip and after-scale if limits)
    log and interp to have limits at 0,1 (add pre-clip and after-scale if limits)

- Test with real colors
- Finish the cdic converter
- Investigate behavior of the log and interpolation things.
- Make workable jsons
- Make workable interps in a folder
