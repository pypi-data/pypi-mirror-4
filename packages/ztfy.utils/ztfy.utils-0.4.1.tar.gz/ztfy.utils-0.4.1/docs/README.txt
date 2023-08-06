==================
ztfy.utils package
==================

.. contents::

What is ztfy.utils ?
====================

ztfy.utils is a set of classes and functions which can be used to handle many small operations.

Internal sub-packages include :
 - date : convert dates to unicode ISO format, parse ISO datetime, convert date to datetime
 - request : get current request, get request annotations, get and set request data via annotations
 - security : get unproxied value of a given object ; can be applied to lists or dicts
 - timezone : convert datetime to a given timezone ; provides a server default timezone utility
 - traversing : get object parents until a given interface is implemented
 - unicode : convert any text to unicode for easy storage
 - protocol : utility functions and modules for several nerwork protocols
 - catalog : TextIndexNG index for Zope catalog and hurry.query "Text" query item
 - text : simple text operations and text to HTML conversion
 - html : HTML parser and HTML to text converter
 - file : file upload data converter
 - tal : text and HTML conversions for use from within TAL


How to use ztfy.utils ?
=======================

A set of ztfy.utils usage are given as doctests in ztfy/utils/doctests/README.txt
