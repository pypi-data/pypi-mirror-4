=============
SimpleMapPlot
=============

This package allows you to easily create a colored map of US States or counties.  For example::

    import simplemapplot

    example_colors = ["#FC8D59","#FFFFBF","#99D594"]
    state_value = {"TX":2, "WI":1, "IL":1, "AK":0, "MI":0, "HI":2}
    make_us_state_map(data=state_value, colors=example_colors)

This creates a colored US state map (SVG file) in the same directory.

Installing
============

Simply use pip::

    pip install SimpleMapPlot

Other Examples
==============

Create a colored world map::

    import simplemapplot

    example_colors = ["#FC8D59","#FFFFBF","#99D594"]
    country_value = {"us":1, "au":2, "gb":0}
    make_world_country_map(data=country_value, colors=example_colors)

