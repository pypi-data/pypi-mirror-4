cifilter
========

:author: Jonathan Wight <jwight@mac.com>
:description: CoreImage filter tool

Goal
----

cifilter is a command line tool for filtering images using CoreImage.

Install
-------

Install from source::

  $ python setup.py install

With pip:

  $ pip install cifilter

With setuptools_::

  $ easy_install -U cifilter

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools

Usage
-----

Note most of the arguments of the form --inputXXXX vary depending on the filter selected.

  $ cifilter --filter CIRippleTransition --help
  Usage: cifilter --filter CIRippleTransition [options]

  Options:
    --version             show program's version number and exit
    -h, --help            Help!
    -i INPUT, --inputImage=INPUT
                          The input image (or - for stdin)
    -o OUTPUT, --outputImage=OUTPUT
                          The output image (or - for stdout)
    -f FILTER, --filter=FILTER
                          Name of the filter
    --listfilters         List available CoreImage filters
    --listcategories      List available CoreImage filter categories
    --category=CATEGORY   Category used to filter listfilter results
    --width=WIDTH         Desired width of output image
    --height=HEIGHT       Desired height of output image
    --type=TYPE           Desired UTI type of output image (e.g. public.png,
                          public.jpg, etc)
    -v, --verbose         Set the log level to INFO
    --loglevel=LOGLEVEL   set the log level, 0 = no log, 10+ = level of logging
    --logfile=LOG_FILE    File to log messages to. If - or not provided then
                          stdout is used
    --open                Open the output image after processing
    --inputTargetImage=VALUE
                          The target image for a transition.
    --inputShadingImage=VALUE
                          An image that looks like a shaded sphere enclosed in a
                          square image.
    --inputCenter=VALUE   The x and y position to use as the center of the
                          effect
    --inputExtent=VALUE   A rectangle that defines the extent of the effect.
    --inputTime=VALUE     The parametric time of the transition. This value
                          drives the transition from start (at time 0) to end
                          (at time 1).
    --inputWidth=VALUE    The width of the ripple.
    --inputScale=VALUE    A value that determines whether the ripple starts as a
                          bulge (higher value) or a dimple (lower value).

Examples
--------

  $ cifilter --help

  $ cifilter --listcategories

  $ cifilter --listfilters

  $ cifilter --listfilters --category CICategoryGenerator

  $ cifilter --filter CIStarShineGenerator --help

  $ cifilter --filter CIEdges < test.jpg

  $ cifilter --filter CIEdgeWork < input.png > output.png

  $ cifilter --filter CIEdgeWork --inputImage 1.png --output 2.png

  $ cifilter --filter CISunbeamsGenerator --open

  $ cifilter --filter CICheckerboardGenerator -o - | cifilter --filter CIEdgeWork -i - --open

  $ cifilter --filter CICheckerboardGenerator --type public.jpeg --outputImage ~/Desktop/Checkerboard.jpg

  $ cifilter --filter CIConstantColorGenerator --inputColor=1.0,1.0,1.0,1.0 --width 256 --height 256 --open

  $ cifilter --filter CIConstantColorGenerator --inputColor=1.0,0.0,0.0,1.0 -o - | cifilter --filter CIHueAdjust --inputAngle=180 --open

Bugs
----

Send all bug reports to jwight@mac.com

