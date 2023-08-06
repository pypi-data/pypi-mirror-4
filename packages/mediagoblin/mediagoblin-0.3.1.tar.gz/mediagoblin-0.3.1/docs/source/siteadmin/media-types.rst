.. MediaGoblin Documentation

   Written in 2011, 2012 by MediaGoblin contributors

   To the extent possible under law, the author(s) have dedicated all
   copyright and related and neighboring rights to this software to
   the public domain worldwide. This software is distributed without
   any warranty.

   You should have received a copy of the CC0 Public Domain
   Dedication along with this software. If not, see
   <http://creativecommons.org/publicdomain/zero/1.0/>.

.. _media-types-chapter:

====================
Media Types
====================

In the future, there will be all sorts of media types you can enable,
but in the meanwhile there are three additional media types: video, audio
and ascii art.

First, you should probably read ":doc:`configuration`" to make sure
you know how to modify the mediagoblin config file.


Enabling Media Types
====================

Media types are enabled in your mediagoblin configuration file, typically it is
created by copying ``mediagoblin.ini`` to ``mediagoblin_local.ini`` and then
applying your changes to ``mediagoblin_local.ini``. If you don't already have a
``mediagoblin_local.ini``, create one in the way described.

Most media types have additional dependencies that you will have to install.
You will find descriptions on how to satisfy the requirements of each media type
on this page.

To enable a media type, edit the ``media_types`` list in your
``mediagoblin_local.ini``. For example, if your system supported image and
video media types, then the list would look like this::

    media_types = mediagoblin.media_types.image, mediagoblin.media_types.video

How does MediaGoblin decide which media type to use for a file?
===============================================================

MediaGoblin has two methods for finding the right media type for an uploaded
file. One is based on the file extension of the uploaded file; every media type
maintains a list of supported file extensions. The second is based on a sniffing
handler, where every media type may inspect the uploaded file and tell if it
will accept it.

The file-extension-based approach is used before the sniffing-based approach,
if the file-extension-based approach finds a match, the sniffing-based approach
will be skipped as it uses far more processing power.


Video
=====

To enable video, first install gstreamer and the python-gstreamer
bindings (as well as whatever gstremaer extensions you want,
good/bad/ugly).  On Debianoid systems::

    sudo apt-get install python-gst0.10 gstreamer0.10-plugins-{base,bad,good,ugly} \
        gstreamer0.10-ffmpeg


Now you should be able to submit videos, and mediagoblin should
transcode them.

.. note::

   You almost certainly want to separate Celery from the normal
   paste process or your users will probably find that their connections
   time out as the video transcodes.  To set that up, check out the
   ":doc:`production-deployments`" section of this manual.


Audio
=====

To enable audio, install the gstreamer and python-gstreamer bindings (as well
as whatever gstreamer plugins you want, good/bad/ugly), scipy and numpy are
also needed for the audio spectrograms.
To install these on Debianoid systems, run::

    sudo apt-get install python-gst0.10 gstreamer0.10-plugins-{base,bad,good,ugly} \
        gstreamer0.10-ffmpeg python-numpy python-scipy

The ``scikits.audiolab`` package you will install in the next step depends on the
``libsndfile1-dev`` package, so we should install it.
On Debianoid systems, run::

    sudo apt-get install libsndfile1-dev

Then install ``scikits.audiolab`` for the spectrograms::

    ./bin/pip install scikits.audiolab

Add ``mediagoblin.media_types.audio`` to the ``media_types`` list in your
``mediagoblin_local.ini`` and restart MediaGoblin. You should now be able to
upload and listen to audio files!


Ascii art
=========

To enable ascii art support, first install the
`chardet <http://pypi.python.org/pypi/chardet>`_
library, which is necessary for creating thumbnails of ascii art::

    ./bin/easy_install chardet


Next, modify (and possibly copy over from ``mediagoblin.ini``) your
``mediagoblin_local.ini``.  In the ``[mediagoblin]`` section, add
``mediagoblin.media_types.ascii`` to the ``media_types`` list.

For example, if your system supported image and ascii art media types, then
the list would look like this::

    media_types = mediagoblin.media_types.image, mediagoblin.media_types.ascii

Now any .txt file you uploaded will be processed as ascii art!
