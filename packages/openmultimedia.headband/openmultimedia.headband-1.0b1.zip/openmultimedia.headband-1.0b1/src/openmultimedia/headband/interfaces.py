from zope import schema
from zope.interface import Interface


class ISettings(Interface):
    """ Define settings data structure """

    image = schema.Bytes(title=u"Image",
                         description=u"",
                         required=False)


class IHeadBandLayer(Interface):
    """ A layer specific to this product.
        this layer is registered using browserlayer.xml in the package
        default GenericSetup profile
    """
