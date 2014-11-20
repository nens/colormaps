todo
====

dict init
---------
Here we just initialize from a general dictionary that specifies:
    At least:
    - class (gradient, discrete)
    - colors
    - values
    Optional:
    - size: 256
    - log: False
    - converter: {sources: targets}

json init
---------

In the colormap json, this translates to:
    class: discrete
    items: [{value: 0, color: [0, 0, 0, 0]}]
    size: 1024
    log: true
    interp: 'ahn2'
and the converter json:
    [{value: 0, color: [0, 0, 0, 0]}]
