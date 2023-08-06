from zope.interface import Interface

class IApogeeBrowserView(Interface):
    """Apogee Browser View"""

    def upload(self):
        """Upload a file to the zodb"""
