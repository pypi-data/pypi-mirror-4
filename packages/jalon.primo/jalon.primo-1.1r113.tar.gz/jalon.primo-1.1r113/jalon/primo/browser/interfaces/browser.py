from zope.interface import Interface

class IPrimoBrowserView(Interface):
    """Primo Browser View"""

    def upload(self):
        """Upload a file to the zodb"""
