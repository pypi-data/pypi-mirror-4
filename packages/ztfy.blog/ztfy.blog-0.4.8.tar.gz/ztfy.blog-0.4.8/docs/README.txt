=================
ztfy.blog package
=================

.. contents::

What is ztfy.blog ?
===================

ztfy.blog is a set of modules which allows easy management of a simple web site based on Zope3
application server.

It's main goal is to be simple to use and manage.

So it's far from being a "features full" environment, but available features currently include:
 - a simple management interface
 - sites, organized with sections and internal blogs
 - topics, made of custom elements (text or HTML paragraphs, resources and links)
 - a default front-office skin.

All these elements can be extended by registering a simple set of interfaces and adapters, to create a
complete web site matching your own needs.

A few list of extensions is available in several packages, like ztfy.gallery which provides
basic management of images galleries in a custom skin, or ztfy.hplskin which provides another skin.


How to use ztfy.blog ?
======================

ztfy.blog usage is described via doctests in ztfy/blog/doctests/README.txt
