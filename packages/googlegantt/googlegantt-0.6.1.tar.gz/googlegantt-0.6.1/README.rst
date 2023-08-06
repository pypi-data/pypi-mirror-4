==============================================
googlegantt - A Google Charts Gantt Chart API
==============================================

Author: Adam Bard, http://adambard.com/

This api is designed to allow you to easily and quickly create gantt
charts using the Google Charts API.  You can save them as images or
just produce a URL.

It works swell as long as you want things measured in days.

The method of producing such a chart is heavily influenced by this post_
by Dave Goerlich. Thanks, Dave.

Quick Start Example
---------------------

::

    from googlegantt import GanttChart, GanttCategory

    gc = GanttChart('Test Chart', width=650, height=200, progress=(2011, 02, 27))

    on_time = GanttCategory('On Time', '0c0')
    late = GanttCategory('Late', 'c00')
    upcoming = GanttCategory('Upcoming', '00c')

    t1 = gc.add_task('Late Task', (2011, 02, 20), (2011, 02, 25), category=late)
    t2 = gc.add_task('On Time Task', depends_on=t1, duration=3, category=on_time)
    t3 = gc.add_task('Future Task', depends_on=t2, duration=7, category=upcoming)

    url = gc.get_url()
    image = gc.get_image()

Produces:

.. image:: https://chart.googleapis.com/chart?chxt=x,y&chds=0,15&chco=FFFFFF00,CC0000FF,00CC00FF,0000CCFF&chbh=46,4,0&chtt=Test%20Chart&chxl=0:|20/02|21/02|22/02|23/02|24/02|25/02|26/02|27/02|28/02|01/03|02/03|03/03|04/03|05/03|06/03|07/03|1:|Future%20Task|On%20Time%20Task|Late%20Task&chdl=|Late|On%20Time|Upcoming&chd=t:0,5,8|5,0,0|0,3,0|0,0,7&chg=6.66666666667,0&chm=r,4D89F933,0,0,0.466666666667&chs=650x200&cht=bhs

Features
--------------------

* Optional Progress indicator shades the elapsed area of the chart.
* Flexible chart width and height.
* Specify task colors using css rules.
* Flexibly specify dates using datetime.date objects, or tuples.
* Produce a Google Chart url, or a png image (requires PIL_).
* Date span is automatically computed from tasks.


Classes
----------------

There are 3 primary classes involved in the creation of a chart.

GanttChart
~~~~~~~~~~~

**GanttChart(title,[ **kwargs])**

    Produce a Gantt Chart.

    Keyword Arguments:

    * **width** The width of the chart.
    * **height** The height of the chart.
    * **progress** A date representing the current time, to produce a shaded 'elapsed' region.

    Example initialization::

        gc = GanttChart('Test Chart', width=600, height=200, progress=(2011, 02, 27))

Methods:

* **GanttChart.get_url()** Get a Google Charts URL of the chart, for direct access
* **GanttChart.get_image()** Get a PIL_ Image object, to be manipulated
* **GanttChart.get_image(save_path)** Save a .png image to *save_path*

GanttCategory
~~~~~~~~~~~~~~

Optional in common usage. Represents a class of Tasks with a color and a title.

**GanttCategory(title[, color])**

    Produce a category object with a given *color*.  Color is specified using a hex string,
    and will be converted to an 8-byte rgba hex color string expected by Google Charts from any
    of the following formats:

    * 3-byte, e.g. 'f00' => 'FF0000FF'
    * 4-byte, e.g. 'f00c' => 'FF0000CC'
    * 6-byte, e.g. 'ff0000' => 'FF0000FF'
    * 8-byte

GanttTask
~~~~~~~~~~

Represents a single bar in the chart.  Must have a specified start and end date, although
these can be computed in different ways.

**GanttTask(title[, start_date=None, end_date=None[, **kwargs]])**

    Keyword Arguments:

    * **start_date** The start date of the task
    * **end_date** The end date of the task
    * **duration** The duration, in days, of the task. May be used instead of *end_date*
    * **depends_on** A GanttTask that must be completed before this one can begin. May be used instead of *start_date*
    * **category** A GanttCategory to apply to this task.
    * **color** A quick way to specify color.  Don't use this when you have categories declared, you will get blank legend entries.

    Either *start_date* or *depends_on* **must** be specified.  Same with *end_date* and *duration*.

    If both *start_date* and *depends_on* are specified, *depends_on* is used.

    If both *end_date* and *duration* are specified, *duration* is used.

More Information
-------------------

Check out the doctests in the gantt.py file for more information.

License
------------

Copyright (c) 2011 Adam Bard (adambard.com)

Licensed under the MIT License: http://www.opensource.org/licenses/mit-license

.. _post: http://www.designinginteractive.com/code/how-to-build-a-gantt-chart-with-the-google-charts-api/
.. _PIL: http://www.pythonware.com/products/pil/
