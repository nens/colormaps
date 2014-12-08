colormaps
=========

Introduction
------------

Transform data into rgba data using discrete lookup tables or color
gradients.

Usage
-----

Create a discrete colormap with the same two colors::
    
    >>> import colormaps
    >>> colormap = colormaps.DiscreteColormap(
    ...     data=[(0, (255, 0, 0, 255)),         
    ...           (1, (0, 0, 255, 127))],
    ...     masked=(255, 0, 0, 255),
    ...     invalid=(0, 255, 0, 255),
    ... )

Create a gradient colormap from red to semi-transparent blue::
    
    >>> import colormaps
    >>> colormap = colormaps.GradientColormap(
    ...     data=[(0, (255, 0,   0, 255)),
    ...           (1, (  0, 0, 255, 127))],
    ...     size=2048,
    ...     masked=(0, 0, 255, 255),
    ... )                                     

Where size is the amount of entries in the prepared look-up table.

Calculate the value a some positions::

    >>> colormap([0, 0.5, 1])
    array([[255,   0,   0, 255],
           [128,   0, 127, 190],
           [  0,   0, 255, 127]], dtype=uint8)


Register the colormap for use in other places::

    >>> colormap.register('my_gradient')
    >>> colormaps.get('my_gradient')
    <colormaps.core.GradientColormap object at 0x7f3a52eb8fd0>

Use a collection of predefined colors using a manager::
    
    >>> manager = colormaps.Manager()
    >>> manager.get('jet')
    >>> m.registered.keys()[:3]
    [u'Spectral', u'summer', u'coolwarm']

Or use your own collection::
    >>> manager = colormaps.Manager('path/to/my/colormap/collection')

The path should point to a folder with files like this::

    {
      "type": "GradientColormap",
      "data": [
          [0.000, [  0,   0,   0, 255]],
          [0.700, [255, 255, 255, 0]],
          [1.000, [255, 255, 255, 255]]
      ]
    }
