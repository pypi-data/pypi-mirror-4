============
django-cufon
============

Easy Cufon with Django.  Django-cufon provides easy-to-use template tags for use with rendering Cufon text in your
HTML with Django.

It provides:

* A tag named ``{% cufon-script %}`` that includes the Cufon JavaScripts.  This is meant to be put in ``HEAD``.
* A tag named ``{% cufon %}`` that handles rendering your Cufon texts.

`read the docs`_ for more information.

.. _`read the docs`: http://django-cufon.rtfd.org

Example
=======

In your ``HEAD`` be sure to include the Cufon scripts and your fonts::

    {% load cufon %}
    <html>
    <head>
        <title>My awesome page</title>
        {% cufon-script %}
        <script language="text/javascript" src="{{ STATIC_URL }}fonts/my_cufon_font.js"></script>
        [...]

Then, in your body where you want to Cufon some text::

    <h1>{% cufon "All your base are belong to us!" "MyAwesomeFont" %}</h1>

The above example will render the text ``All your base are belong to us!`` in the Cufon font called ``MyAwesomeFont``

Documentation
=============

For a little more documentation, though not much more, see the ``docs`` folder or `read the documentation online`_

.. _`read the documentation online`: http://django-cufon.rtfd.org

Authors & Special Thanks
========================

django-cufon was written by `Jonathan Enzinna`_

Many special thanks to `Simo Kinnunen`_ for creating `Cufon`_ in the first place.

.. _`Jonathan Enzinna`: https://github.com/JonnyFunFun
.. _`Simo Kinnunen`: https://twitter.com/sorccu
.. _`Cufon`: http://cufon.shoqolate.com/generate/