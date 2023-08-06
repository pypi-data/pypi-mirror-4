========
Overview
========

*This package is at present not reusable without depending on a large
chunk of the Zope Toolkit and its assumptions. It is maintained by the*
`Zope Toolkit project <http://docs.zope.org/zopetoolkit/>`_.

This package provides a "page template" resource class, a resource which
content is processed with Zope Page Templates engine before returning to
client.

The resource factory class is registered for "pt", "zpt" and "html" file
extensions in package's ``configure.zcml`` file.
