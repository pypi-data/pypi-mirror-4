.. contents::

Introduction
============

ZTFY.sequence is a small package used to set sequential identifiers on selected persistent
contents.

The SequentialIntIds utility is based on zope.intid.IntIds utility, but overrides a few methods
to be able to define these sequential IDs.

Classes for which we want to get these sequential IDs have to implement the ISequentialIntIdTarget
marker interface. They can also implement two attributes, which allows to define the name of
the sequence to use and a prefix.

This prefix, which can also be defined on the utility, is used to define an ID in hexadecimal
form, as for example 'LIB-IMG-000012ae7c', based on the 'main' numeric ID.


Sequence utility
================

Sequences are handled by a utility implementing ISequentialIntIds interface and registered for
that interface.

You can set two optional parameters on this utility, to define the first hexadecimal ID prefix
as well as the length of hexadecimal ID (not including prefix).
