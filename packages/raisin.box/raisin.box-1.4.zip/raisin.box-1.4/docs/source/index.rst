Welcome to raisin.box's documentation!
======================================

The raisin.box package is a part of Raisin, the web application used for 
publishing the summary statistics of Grape, a pipeline used for processing
and analyzing RNA-Seq data.

This package contains the definition of the boxes that appear on the pages rendered by
Pyramid.

All boxes have a method for augmenting their configuration dynamically in::

    boxes.py

An example of augmenting just the basics, like the title, description and description type::

    @augment((PICKLED,))
    def project_about(self, box):
        box['title'] = 'About'
        box['description'] = box[PICKLED]['description']       
        box['description_type'] = 'infotext'
        return box       

An example of correcting the height of a chart depending on the length of the table data::

    @augment((JSON, PICKLED))
    def read_quality(self, box):
        # Need to extract some infos from the table, so load the pickled dictionary
        table = box[PICKLED]
        height = max(len(table['table_data']) * 60, 160)
        box['chartoptions']['height'] = str(height)

The augment decorator
---------------------

The augment decorator defines what resource representations should be fetched.

* JSON

    * Needed for charts that rely on Google visualization tools

* PICKLED

    * Needed if your method needs access to the Python dictionary representation of a resource

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
