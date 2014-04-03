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
    ...     values=(0, 1),                      
    ...     colors=((255, 0, 0, 255),         
    ...             (0, 0, 255, 127)),        
    ... )                                     

Create a gradient colormap from red to semi-transparent blue::
    
    >>> import colormaps
    >>> colormap = colormaps.GradientColormap(
    ...     stops=(0, 1),                      
    ...     colors=((255, 0, 0, 255),         
    ...             (0, 0, 255, 127)),        
    ... )                                     

Calculate the value a some positions::

    >>> colormap([0, 0.5, 1])
    array([[255,   0,   0, 255],
           [128,   0, 127, 191],
    [  0,   0, 255, 127]], dtype=uint8)


Register the colormap for use in other places::

    >>> colormap.register('my_gradient')
    >>> colormaps.get('my_gradient')
    <colormaps.core.GradientColormap object at 0x7f3a52eb8fd0>
 

Todo
----

- Add matplotlib colormaps
- Add specific nens colormaps
- Add utils for conversion of hex and float colors
- Add Docstrings
