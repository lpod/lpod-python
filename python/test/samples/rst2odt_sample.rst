========================
Wiki Syntax in 3 Minutes
========================

.. contents::

A title is made by underlining
==============================

Use different underlines for subtitles
--------------------------------------

To break paragraphs, just separate them with an empty line.

Another paragraph.

- a list using dash sign
- a link to a website: http://hforge.org
- a link to another page of the wiki: `FrontPage`_
- a sublist

  * a list using star sign
  * write in *italic*, in **bold** or in ``monotype``

.. figure:: image.png
  :width: 100

  Here is the caption of this image reduced to 100 pixels in width.
  You can click on `/ui/aruni/images/logo.png`_ to see it full size.

You can include snippets without wiki interpretation:

::

  class Module(Folder):

    def view(self):
      print u"Hello, world!"

    `This will not be interpreted`_

For a list of all possibilities like footnotes, tables, etc. `see the
documentation`_. You can also use the toolbar.

.. _`see the documentation`:
   http://docutils.sourceforge.net/docs/user/rst/quickref.html


