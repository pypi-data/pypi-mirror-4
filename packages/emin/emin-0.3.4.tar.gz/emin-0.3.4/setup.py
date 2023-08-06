#! /usr/bin/env python

"""\
emin makes static Web pages for presenting lots of imagey things: photos, PDFs,
graphs with thumbnails as well as links to the image/doc file proper.

It's primarily intended for making Web photo galleries for the sorts of people
who don't want to install some PHP monstrosity just to put their photos
online. On the assumption that most people will want to tweak their gallery's
appearance, the output is fully customisable using the Cheetah templating
engine.

Supported image formats are JPEG, PNG, GIF, TIFF, PDF and EPS, with the latter
two being converted to PNG for Web display.  Image resizing, renaming and
thumbnailing is supported, as is building a zip file to download the whole
set. Large image sets can be split over several pages.
"""

## Get setuptools stuff
from distutils.core import setup


## Try to import Cheetah templating
try:
    from Cheetah.Template import Template
except Exception, e:
    logging.error("Couldn't import required Cheetah package: please install Cheetah first")
    exit(1)

## Try to import Python Imaging Library
try:
    import PIL.Image
except Exception, e:
    logging.error("Couldn't import required Python Imaging Library package: please install PIL first")
    exit(1)


## Setup definition
setup(name = 'emin',
      version = "0.3.4",
      scripts = ['emin'],
      requires = ["Cheetah", "PIL"],
      author = 'Andy Buckley',
      author_email = 'andy@insectnation.org',
      #url = 'http://www.insectnation.org/projects/emin/',
      description = 'A simple builder of static Web galleries.',
      long_description = __doc__,
      keywords = 'photo gallery web www html template',
      license = 'GPL',
      classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python']
      )
