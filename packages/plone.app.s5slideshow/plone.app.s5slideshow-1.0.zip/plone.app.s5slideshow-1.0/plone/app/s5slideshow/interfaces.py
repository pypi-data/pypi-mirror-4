from zope.interface import Interface


class IS5SlideshowLayer(Interface):
    """Browser layer for this package.

    This is applied to the request when this package is activated,
    which lets us enable the schema extender only for Plone sites
    that have the package activated.
    """


class IPresentationMode(Interface):
    """Marker for content that supports presentation mode.

    By default this is applied to ATDocument in configure.zcml.
    """
