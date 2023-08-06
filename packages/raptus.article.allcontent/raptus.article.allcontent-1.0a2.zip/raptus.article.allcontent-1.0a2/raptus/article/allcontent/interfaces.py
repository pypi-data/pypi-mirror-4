from zope.interface import Interface

class IAllcontentStyleProvider(Interface):
    """ A provider for CSS classes used in the all content component
        
        The provided classes may be selected by nested articles and
        the selected ones are added to the div-tag surrounding the
        articles content.
    """
    
    def classes():
        """ Returns a list of class, title tuples
        """
