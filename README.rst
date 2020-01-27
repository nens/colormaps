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

Calculate the value at some positions::

    >>> colormap([0, 0.5, 1])
    array([[255,   0,   0, 255],
           [127,   0, 127, 190],
           [  0,   0, 255, 127]], dtype=uint8)


Register the colormap for use in other places::

    >>> colormap.register('my_gradient')
    >>> colormaps.get('my_gradient')
    <GradientColormap: size 2048, limits 0 - 1, log False, interp False>

Use a collection of predefined colors using a manager::
    
    >>> manager = colormaps.Manager()
    >>> manager.get('jet')
    <GradientColormap: size 256, limits 0.0 - 1.0, log False, interp False>

    >>> sorted(manager.registered.keys())[:3]
    ['Accent', 'Accent_r', 'Blues']

Or use your own collection::

    >>> manager = colormaps.Manager('path/to/my/colormap/collection')

The path should point to a folder with json-files ('my-colormap.json')
containing the kwargs for colormaps.create() like this::

    {
      "type": "GradientColormap",
      "data": [
          [0.000, [  0,   0,   0, 255]],
          [0.700, [255, 255, 255, 0]],
          [1.000, [255, 255, 255, 255]]
      ]
    }


Development installation
------------------------

For development, you can use a docker-compose setup::

    $ docker-compose build --build-arg uid=`id -u` --build-arg gid=`id -g` lib
    $ docker-compose up --no-start
    $ docker-compose start
    $ docker-compose exec lib bash

Create & activate a virtualenv::

    (docker)$ virtualenv .venv
    (docker)$ source bin/activate

Install stuff and run the tests::

    (docker)(virtualenv)$ pip install -r requirements.txt
    (docker)(virtualenv)$ pytest

Update packages::
    
    (docker)$ rm -rf .venv
    (docker)$ virtualenv .venv
    (docker)$ source bin/activate
    (docker)(virtualenv)$ pip install -e .[test]
    (docker)(virtualenv)$ pip freeze > requirements.txt

