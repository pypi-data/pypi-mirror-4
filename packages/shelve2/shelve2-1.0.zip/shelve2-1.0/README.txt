shelve2 -- An expanded shelve module
====================================

Introduction
------------
The ``shelve`` shipped in the Python Standard Library is a very easy-to-use
module to store arbitrary Python objects in a key-value database. However, it
can only use the ``pickle`` module for serialisation which is unsafe because
deserialising untrusted data may execute arbitrary code.

The ``shelve2`` module is a fully compatible version of the ``shelve`` module
that was expanded to support additional serialisation protocol choices.
Specifically, JSON serialisation was added to provide a safer option -- at the
cost of being able to store almost any arbitrary Python object. On top of that,
other serialiser implementations can be supported without touching the module
source.


API Overview
------------
The interface of the ``shelve`` module is fully supported and un-changed;
``shelve2`` is a drop-in replacement. However, to use protocols other than
pickle, you need to use the newly-added API. A short overview of the new
interface members is given below. More information can be found in the module's
docstrings.

AbstractShelf
  New base class that implements all of the behaviour of ``Shelf`` but performs
  serialisation and deserialisation using the abstract ``_dump`` and ``_load``
  methods. These need to be provided in a derived class (preferably using a
  mixin class).

AbstractBsdDbShelf
  Abstracted version of ``BsdDbShelf``.

AbstractDbfilenameShelf
  Abstracted version of ``DbfilenameShelf``.

The original ``*Shelf`` classes are implemented as subclasses of their
``Abstract*Shelf`` counterpart.

PickleMixin
  A serialisation mixin that uses the ``pickle`` module. Used in the ``*Shelf``
  classes to provide the original behaviour for those.

JsonMixin
  A serialisation mixin using the ``json`` module.

open2
  An expanded version of the ``shelve.open`` function. It supports an additional
  ``serialisation_protocol`` parameter to pick a serialiser implementation.


Copyright and License Information
---------------------------------
This module (and its unit tests) are based on the ``shelve`` module from the
Python Standard Library which is distributed under the terms of the
Python Software Foundation License Version 2. This module is distributed under
these same terms.

``shelve2`` changes are Copyright (c) 2013 Felix Krull

Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011
 2012, 2013 Python Software Foundation. All rights reserved.
Copyright (c) 2000 BeOpen.com. All rights reserved.
Copyright (c) 1995-2001 Corporation for National Research Initiatives. All
 rights reserved.
Copyright (c) 1991-1995 Stichting Mathematisch Centrum. All rights reserved.

1. This LICENSE AGREEMENT is between the Python Software Foundation
("PSF"), and the Individual or Organization ("Licensee") accessing and
otherwise using this software ("Python") in source or binary form and
its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
analyze, test, perform and/or display publicly, prepare derivative works,
distribute, and otherwise use Python alone or in any derivative version,
provided, however, that PSF's License Agreement and PSF's notice of copyright,
i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013 Python Software Foundation; All Rights Reserved" are retained
in Python alone or in any derivative version prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on
or incorporates Python or any part thereof, and wants to make
the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to Python.

4. PSF is making Python available to Licensee on an "AS IS"
basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any
relationship of agency, partnership, or joint venture between PSF and
Licensee.  This License Agreement does not grant permission to use PSF
trademarks or trade name in a trademark sense to endorse or promote
products or services of Licensee, or any third party.

8. By copying, installing or otherwise using Python, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.
