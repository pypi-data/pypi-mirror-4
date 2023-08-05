""" Sparql Data Provenance

    >>> portal = layer['portal']
    >>> from eea.app.visualization.interfaces import IDataProvenance

"""

class SparqlDataProvenance(object):
    """
    Sparql data provenance metadata accessor/mutator

        >>> doc = portal.invokeFactory('Sparql', 'sparql')
        >>> doc = portal._getOb(doc)
        >>> source = IDataProvenance(doc)
        >>> source
        <eea.sparql.data.source.SparqlDataProvenance object...>

    """
    def __init__(self, context):
        self.context = context
    #
    # Title
    #
    @property
    def title(self):
        """
        Sparql data source title

        Source title shares the same field as obj.title

            >>> doc.setTitle('A Sparql')
            >>> source.title
            'A Sparql'

        """
        return self.context.title_or_id()

    @title.setter
    def title(self, value):
        """
        Sparql data source link setter.

        You can't change title from here. It's read-only.

            >>> source.title = u'GDP vs. GHG'
            >>> source.title
            'A Sparql'

            >>> doc.title_or_id()
            'A Sparql'

        """
        return
    #
    # Link
    #
    @property
    def link(self):
        """
        Sparql data source link

        Source link shares the same link as obj.absolute_url

            >>> source.link
            'http://nohost/plone/sparql'

        """
        return self.context.absolute_url()

    @link.setter
    def link(self, value):
        """
        Sparql data source link setter

        You can't change title from here. It's read-only.

            >>> source.link = u'http://daviz.eionet.europa.eu'
            >>> source.link
            'http://nohost/plone/sparql'

        """
        return
    #
    # Owner
    #
    @property
    def owner(self):
        """
        Sparql data source owner.

        Source owner shares the enpoint_url field

            >>> source.owner
            ''

            >>> mutator = doc.getField('endpoint_url').getMutator(doc)
            >>> mutator('http://cr.eionet.europa.eu/sparql')

            >>> source.owner
            'http://cr.eionet.europa.eu/sparql'

        """
        return self.context.getField('endpoint_url').getAccessor(self.context)()

    @owner.setter
    def owner(self, value):
        """
        Sparql data source owner setter.

        You can't change owner from here. It's read-only.

            >>> source.owner = u'EEA'
            >>> source.owner
            'http://cr.eionet.europa.eu/sparql'

        """
        return
