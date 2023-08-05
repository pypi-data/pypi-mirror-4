tt_sass
=======
Collection of `Sass`_ styles and mixins for use at the `Texas Tribune`_.


Installation and Configuration
------------------------------
You can install this using `pip`_ like this:

::

    pip install tt_sass

Once installed, you need to add it to your ``INSTALLED_APPS``.  You can do that
however you like or you can copy-and-paste this in after your ``INSTALLED_APPS``
are defined.

::

    INSTALLED_APPS += ['tt_sass', ]

``tt_sass`` relies on `django-staticfiles`_ in order to work.  You must run
the ``collectstatic`` command inside your project like this:

::

    python manage.py collectstatic --link

Remember, you must re-run this command any time you add new staticfiles.

Now you're ready to start using ``tt_sass``.


Usage
-----
You can use this inside your Sass by adding the following:

::

    @import "tt_sass/texastribune"

Once you've done that, you need to compile your Sass.  Assuming you're using the
default Texas Tribune setup of having a ``static`` directory at your project root,
you should run the following:

::

    sass --load-path=static/ --watch --poll --compass static

This command setups up the path correctly for all of your code and watches the
file for changes.


Using the Grid
""""""""""""""
The grid is based off of `Chris Coyer's`_ `simple grid`_.  The syntax has been
changed around a little bit and it's been mixinified, but the concept is the
same.

To create a grid, similar to a row in frameworks like Foundation and Bootstrap,
you use the ``.grid`` class.  Inside a grid, you add cells and tell them how far
to span.  For example, you do this to create a grid with 12 columns (the
default) and two cells, one of 8 columns and one of 4 columns:

::

    <div class="grid">
        <div class="cell w-8"></div>
        <div class="cell w-4"></div>
    </div>




Creating a Semantic Grid
""""""""""""""""""""""""
*TODO*


Using the Responsive Mixins
"""""""""""""""""""""""""""
``tt_sass`` provides you with a ``breakpoint`` mixin for handling responsive
design.  It ships with the following breakpoints built-in:

mobile-portrait
    defaults to ``max-width: 320px``
mobile
    defaults to ``max-width: 720px``
tablet
    defaults to ``min-width: 720px``
classic
    defaults to ``min-width: 960px``

You can over ride any of these values by setting a variable by their name prior
to importing ``tt_sass/texastribune``.

You use the mixin like this:

::

    p
        +breakpoint(mobile)
            font-size: 1.2em
        +breakpoint(tablet)
            font-size: 1.1em
        +breakpoint(classic)
            font-size: 1.0em

You can specify an arbitrary breakpoint as well:

::

    div
        +breakpoint("max-width: 500px")
            background-color: red


Various Helpers
"""""""""""""""
*TODO*


Examples
--------
All of these are being documented in the ``example/`` Django project.  See that
directory for instructions on how to run that project.


Contributing
------------
This project is released in hopes that it helps people understand how you might
build your own Sass framework for use in the context of a Django project.  As
such, contributions from those outside the Texas Tribune probably won't be
accepted.


.. _Chris Coyer's: http://chriscoyier.net/
.. _django-staticfiles: http://django-staticfiles.readthedocs.org/en/latest/
.. _pip: http://www.pip-installer.org/en/latest/
.. _Sass: http://sass-lang.com/
.. _simple grid: http://css-tricks.com/dont-overthink-it-grids/
.. _Texas Tribune: http://www.texastribune.org/
