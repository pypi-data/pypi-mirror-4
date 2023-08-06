=================
ztfy.file package
=================

.. contents::

What is ztfy.file ?
===================

ztfy.file is a set of classes to be used with Zope3 application server.
The purpose of this package is to handle :
 - custom schema fields with their associated properties and browser widgets to
   automatically handle fields as external files
 - automatically handle generation of images thumbnails for any image ; these
   thumbnails are accessed via a custom namespace ("++display++w128.jpeg" for example to get
   a thumbnail of 128 pixels width) and are stored via images annotations
 - allow selection of a square part of a thumbnail to be used as a "mini-square thumbnail".

Square thumbnails selection is based on JQuery package extensions, so the ztfy.jqueryui is
required to use all functions of ztfy.file package.


How to use ztfy.file ?
======================

A set of ztfy.file usages are given as doctests in ztfy/file/doctests/README.txt
