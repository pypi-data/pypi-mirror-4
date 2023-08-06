================
python-mediamosa
================

mediamosa is a python wrapper for accessing a mediamosa
(http://www.mediamosa.org) api.

------------
Installation
------------

Install mediamosa as follows:

::

   pip install mediamosa

---------------
Getting Started
---------------

Start by creating a connection to a mediamosa api.

.. code:: python

    >>> from mediamosa.api import MediaMosaAPI
    >>> api = MediaMosaAPI('http://apivideo.ugent.be')
    >>> api.authenticate('USERNAME', 'PASSWORD')
    True

the .authentication() method returns a boolean indicating if the
username and password were accepted by the server.

You can now query your assets

.. code:: python

    >>> api.asset_list()
    [<mediamosa.resources.Asset GAKkgcmMPaIZdMl3dczqUESA>,
    <mediamosa.resources.Asset KWdqPljZge6ESLWbPdEEcG0j>,
    <mediamosa.resources.Asset d1bbGsmEjXmeSfM8PGT5uRjB>,
    <mediamosa.resources.Asset uKgRwHGTidLLiTiSUQu26buN>,
    <mediamosa.resources.Asset x2XRGwefXfNvoRNYLJjfWS5O>,
    <mediamosa.resources.Asset ONZDQiGfhTf8OcsKumKISpOy>,
    <mediamosa.resources.Asset A1lkCZclpXaWSLE9RPK4Pthk>,
    <mediamosa.resources.Asset A2TmfbWMcMU6r8jWHOS2JEsf>,
    <mediamosa.resources.Asset B7zsZXLvnnLCCIyJOrCQxxRl>,
    <mediamosa.resources.Asset C2VNSEfaeMc7ToOeirEqiztz>, ...]

Each direct child of an <item> can be accessed as an attribute:

.. code:: python

    >>> asset = api.asset_list()[0]
    >>> asset.dublin_core.get('title')
    u'big buck bunny '

You can also indiviually request specific assets by querying the api
object:

.. code:: python

    >>> api.asset('ONZDQiGfhTf8OcsKumKISpOy')
    <mediamosa.resources.Asset ONZDQiGfhTf8OcsKumKISpOy>


Mediafiles connected to the asset can also be queried:

.. code:: python

    >>> asset.list_mediafiles()
    [<mediamosa.resources.Mediafile (mp4) Yb8peCXknRXIhimONUUzkuBT>]
    >>> mediafile = asset.list_mediafiles()[0]
    >>> mediafile.filename
    u'bigbuckbunny30sec.mp4'
    >>> mediafile.is_downloadable
    True

You can also individually request mediafiles by querying the api
object:

.. code:: python

    >>> api.mediafile('Yb8peCXknRXIhimONUUzkuBT')
    <mediamosa.resources.Mediafile (mp4) Yb8peCXknRXIhimONUUzkuBT>


Playing a mediafile is done as follows:

.. code:: python

    >>> mediafile.play()
    u'<script type="text/javascript">...'

This will by default return javascript code necessary to play the
mediafile.

------
Errors
------

If anything goes wrong with executing the queries, the API will throw
a mediamosa.api.ApiException.

-------------------------
Bugs and Feature requests
-------------------------

.. warning::
   The API wrapper is in early stages of development and will require a few
   more iterations to be considered stable

For help, issues and feature requests, please go to http://www.github.com/UGentPortaal/python-mediamosa.

------------
Contributing
------------

Pull requests may be submitted to the develop branch at our github
project. Make sure the code and functionality are sufficiently
documented.