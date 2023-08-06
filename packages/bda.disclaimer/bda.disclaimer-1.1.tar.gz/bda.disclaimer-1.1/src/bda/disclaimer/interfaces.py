from zope.interface import Interface


class IDisclaimerLayer(Interface):
    """Layer for the Disclaimer product.
    """


class IDisclaimerText(Interface):

    def __call__():
        """Return the text to be displayed at the disclaimer page.
        """
