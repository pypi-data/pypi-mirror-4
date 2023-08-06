bda.disclaimer
==============

Cookie based access restriction for Plone sites.


Installation
------------

Add ``bda.disclaimer`` to installation dependencies and and install product.


Provide the Disclaimer Text
---------------------------

Disclaimer text is looked up via ``bda.disclaimer.interfaces.IDisclaimerText``
adapter. The default implementation expects an document at Plone Site root with
Id ``disclaimer``. The Body Text of this Document is used as disclaimer
text.


Customizing UI
--------------

To provide your own disclaimer markup, the browser page named ``disclaimer``
must be overwritten.


Copyright and Contributions
---------------------------

Copyright 2008-2013, Blue Dynamics Alliance - http://bluedynamics.com

Author: Robert Niederreiter <rnix [at] squarewave [dot] at>
Contributions: Peter Holzer <hpeter [at] agitator [dot] com>


Changes
-------

1.1
---

- Simplification, port to Plone 4.x
  [rnix]

1.0
---

- Initial work
  [rnix, hpeter]
