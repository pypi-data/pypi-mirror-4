HTML/Javascript Demos
=====================

This document demonstrates usage of the ``demo`` directive.

Regular layout
--------------

.. sourcecode:: rst

   .. demo::

      <button style="color: green">Regular layout</button>

.. demo::

   <button style="color: green">Regular layout</button>

Source first
------------

.. sourcecode:: rst

   .. demo::
      :layout: source, demo

      <button style="color: brown">Source first</button>

.. demo::
   :layout: source, demo

   <button style="color: brown">Source first</button>

Hidden source
-------------

.. sourcecode:: rst

   .. demo::
      :layout: +demo, -source

      <button style="color: red">Hidden source</button>

.. demo::
   :layout: +demo, -source

   <button style="color: red">Hidden source</button>

Hidden demo
-----------

.. sourcecode:: rst

   .. demo::
      :layout: +source, -demo

      <button style="color: magenta">Hidden demo</button>

.. demo::
   :layout: +source, -demo

   <button style="color: magenta">Hidden demo</button>

No source
---------

.. sourcecode:: rst

   .. demo::
      :layout: demo

      <button style="color: blue">No source</button>

.. demo::
   :layout: demo

   <button style="color: blue">No source</button>


