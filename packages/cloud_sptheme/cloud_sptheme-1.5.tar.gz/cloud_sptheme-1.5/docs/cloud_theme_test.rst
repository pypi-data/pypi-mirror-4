.. index:: cloud; feature test

==================
Cloud Feature Test
==================

This page contains examples of various features of the Cloud theme.
It's mainly useful internally, to make sure everything is displaying correctly.

Inline Text
=============

Inline literal: ``literal text``.

External links are prefixed with an arrow: `<http://www.google.com>`_.

But email links are not prefixed: bob@example.com.

Issue tracker link: :issue:`5`.

Admonition Styles
=================
.. note::
    This is a note.

.. warning::

    This is warning.

.. seealso::

    This is a "see also" message.

.. todo::

    This is a todo message.

    With some additional next on another line.

.. deprecated:: XXX This is a deprecation warning.

.. rst-class:: floater

.. note::
    This is a floating note.

Table Styles
============

.. table:: Normal Table

    =========== =========== ===========
    Header1     Header2     Header3
    =========== =========== ===========
    Row 1       Row 1       Row 1
    Row 2       Row 2       Row 2
    Row 3       Row 3       Row 3
    =========== =========== ===========

.. rst-class:: plain

.. table:: Plain Table (no row shading)

    =========== =========== ===========
    Header1     Header2     Header3
    =========== =========== ===========
    Row 1       Row 1       Row 1
    Row 2       Row 2       Row 2
    Row 3       Row 3       Row 3
    =========== =========== ===========

.. rst-class:: centered

.. table:: Centered Table

    =========== =========== ===========
    Header1     Header2     Header3
    =========== =========== ===========
    Row 1       Row 1       Row 1
    Row 2       Row 2       Row 2
    Row 3       Row 3       Row 3
    =========== =========== ===========

.. rst-class:: fullwidth

.. table:: Full Width Table

    =========== =========== ===========
    Header1     Header2     Header3
    =========== =========== ===========
    Row 1       Row 1       Row 1
    Row 2       Row 2       Row 2
    Row 3       Row 3       Row 3
    =========== =========== ===========

.. table:: :doc:`Table Styling Extension <lib/cloud_sptheme.ext.table_styling>`
    :widths: 1 2 3
    :header-columns: 1
    :column-alignment: left center right
    :column-dividers: none single double single
    :column-wrapping: nnn

    =========== =========== ===========
    Width x1    Width x2    Width x3
    =========== =========== ===========
    Header 1    Center 1    Right 1
    Header 2    Center 2    Right 2
    Header 3    Center 3    Right 3
    =========== =========== ===========

.. rst-class:: html-toggle

.. _toggle-test-link:

Toggleable Section
==================
This section is collapsed by default.
But if a visitor follows a link to this section or something within it
(such as :ref:`this <toggle-test-link>`), it will automatically be expanded.

.. rst-class:: html-toggle expanded

Toggleable Subsection
---------------------
Subsections can also be marked as toggleable.
This one should be expanded by default.

.. rst-class:: emphasize-children

Section With Emphasized Children
================================
Mainly useful for sections with many long subsections,
where a second level of visual dividers would be useful.

Child Section
----------------
Should be have slightly lighter background, and be indented.

.. rst-class:: html-toggle

Toggleable Subsection
---------------------
Test of emphasized + toggleable styles. Should be collapsed by default.
