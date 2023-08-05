Overview
--------

collective.sharerizer makes it easy to add a 3rd-party widget to the Plone
document actions area to share a page via various methods.

It does not assume the use of any particular 3rd-party tool, but instead
provides a control panel where the relevant Javascript widget from the desired
tool can be pasted.  Some tools that could be used are `Add to Any`_ and
`ShareThis`_.

.. _`Add to Any`: http://www.addtoany.com/
.. _`ShareThis`: http://sharethis.com/

Configuration
-------------

Install collective.sharerizer via the quick installer or Add/Remove Products
control panel.

Now, in Site Setup, there is a new control panel called Sharerizer Settings.
Here you can paste the Javascript snippet for your sharing widget of choice.

There is also an unrelated option which enables icons for the document actions.
These icons must be configured for each action in the ZMI, within portal_actions.


Compatibility
-------------

collective.sharerizer is compatible with Plone 3 and Plone 4.

It operates by overriding the document actions viewlet, so is not compatible
with other add-ons or themes that do the same thing.


Credits
-------

collective.sharerizer was built by `Groundwire`_.

.. _`Groundwire`: http://groundwire.org
