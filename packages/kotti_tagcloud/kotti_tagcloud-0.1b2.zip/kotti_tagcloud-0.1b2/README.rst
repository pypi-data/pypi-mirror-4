==============
kotti_tagcloud
==============

Tagcloud widget for Kotti.

`Find out more about Kotti`_

Setup
=====

To activate the ``kotti_tagcloud`` add-on in your Kotti site, you need to
add an entry to the ``kotti.configurators`` setting in your Paste
Deploy config.  If you don't have a ``kotti.configurators`` option,
add one.  The line in your ``[app:main]`` (or ``[app:kotti]``, depending on how
you setup Fanstatic) section could then look like this::

    kotti.configurators =
        kotti_settings.kotti_configure
        kotti_tagcloud.kotti_configure

Please note that ``kotti_tagcloud`` depends on kotti_settings, so you have to
list it in your ``kotti.configurators`` too.

``kotti_tagcloud`` extends your Kotti site with a widget where all tags that are
assigned to any content and present it in a tagcloud. The particular tags are
linked with the tag search of Kotti itself. The actual tag widget is build with
`TagCanvas`_ and use `explorercanvas`_ to provide the HTML5 canvas tag also for
the beloved Internet Explorer <= 0.8.

In the settings of ``kotti_tagcloud`` you can choose the slot and the context where
the widget will be shown. Just go to Site Setup -> Settings -> Tagcloud Settings and
adjust it to your needs.


.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
.. _TagCanvas: http://www.goat1000.com/tagcanvas.php
.. _explorercanvas: https://code.google.com/p/explorercanvas/
