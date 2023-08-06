from zope import interface

class IPDFConverter(interface.Interface):
    """ Adapter to convert a view to a PDF using PrinceXML
    """

    def __call__(method='__call__', destination=None):
        """ Returns the contents of the PDF as a stream or
            writes them directly into the provided destination
        """
