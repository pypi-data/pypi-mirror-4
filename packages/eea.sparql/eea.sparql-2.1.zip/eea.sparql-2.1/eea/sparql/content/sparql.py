"""Definition of the Sparql content type
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata, base
from Products.ATContentTypes.content.folder import ATFolder

from Products.Archetypes import atapi
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import TextField, TextAreaWidget
from Products.ZSPARQLMethod.Method import ZSPARQLMethod, \
                                        interpolate_query, \
                                        run_with_timeout, \
                                        query_and_get_result, \
                                        parse_arg_spec, \
                                        map_arg_values
from AccessControl.Permissions import view
from eea.sparql.cache import ramcache, cacheSparqlKey
from eea.sparql.config import PROJECTNAME
from eea.sparql.interfaces import ISparql, ISparqlBookmarksFolder
from eea.versions.interfaces import IVersionEnhanced
from eea.versions import versions

from zope.interface import implements

SparqlBaseSchema = atapi.Schema((
    StringField(
        name='endpoint_url',
        widget=StringWidget(
            label="Sparql endpoint URL",
        ),
        required=1
    ),
    IntegerField(
        name='timeout',
        widget=SelectionWidget(
            label="Timeout (seconds)",
        ),
        default=10,
        required=1,
        vocabulary=['10', '20', '30', '40', '50', '60'],
        accessor='getTimeout',
        edit_accessor='getTimeout',
        mutator='setTimeout'
    ),
    StringField(
        name='arg_spec',
        widget=StringWidget(
            label="Arguments",
        ),
        required=0
    ),
    TextField(
        name='sparql_query',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),

        widget=TextAreaWidget(
            label="Query",
        ),
        required=1
    ),
))

SparqlSchema = getattr(base.ATCTContent, 'schema', Schema(())).copy() + \
        SparqlBaseSchema.copy()

SparqlSchema['title'].storage = atapi.AnnotationStorage()
SparqlSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SparqlSchema, moveDiscussion=False)

SparqlBookmarksFolderSchema = getattr(ATFolder, 'schema', Schema(())).copy() + \
        SparqlBaseSchema.copy()
SparqlBookmarksFolderSchema['sparql_query'].widget.description = \
        'The query should return label, bookmark url, query'

class Sparql(base.ATCTContent, ZSPARQLMethod):
    """Sparql"""
    implements(ISparql, IVersionEnhanced)

    meta_type = "Sparql"
    schema = SparqlSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security = ClassSecurityInfo()

    security.declarePublic('index_html')
    def index_html(self, REQUEST=None, **kwargs):
        """index_html"""
        return self.REQUEST.response.redirect(self.absolute_url()+"/@@view")

    @property
    def query(self):
        """query"""
        return "\n".join(x for x in self.sparql_query().splitlines()
                         if not x.strip().startswith("#"))

    @property
    def query_with_comments(self):
        """query"""
        return self.sparql_query()

    security.declarePublic("execute_query")
    @ramcache(cacheSparqlKey, dependencies=['eea.sparql'])
    def execute_query(self, args=None):
        """execute query"""
        arg_spec = parse_arg_spec(self.arg_spec)
        arg_values = map_arg_values(arg_spec, args)[1]
        return self.execute(**self.map_arguments(**arg_values))

    security.declarePublic("getTimeout")
    def getTimeout(self):
        """timeout"""
        return str(self.timeout)

    security.declarePublic("setTimeout")
    def setTimeout(self, value):
        """timeout"""
        try:
            self.timeout = int(value)
        except Exception:
            self.timeout = 10

    security.declareProtected(view, 'execute')
    def execute(self, **arg_values):
        """
        Override execute from ZSPARQLMethod in order to have a default timeout
        """
        cooked_query = interpolate_query(self.query, arg_values)
        cache_key = {'query': cooked_query}
        result = self.ZCacheable_get(keywords=cache_key)

        if result is None:
            args = (self.endpoint_url, cooked_query)
            result = run_with_timeout(
                max(getattr(self, 'timeout', 10), 10),
                query_and_get_result,
                *args)
            self.ZCacheable_set(result, keywords=cache_key)

        return result


class SparqlBookmarksFolder(ATFolder, Sparql):
    """Sparql Bookmarks Folder"""
    implements(ISparqlBookmarksFolder)
    meta_type = "SparqlBookmarksFolder"
    schema = SparqlBookmarksFolderSchema

    def checkQuery(self, title, endpoint, query):
        """Check if a query already exists
           0 - missing
           1 - exists
           2 - exists but changed"""

        found = False
        changed = True
        for sparql in self.values():
            if sparql.title == title:
                latest_sparql = versions.get_versions_api(
                    sparql).latest_version()
                found = True
                if latest_sparql.query_with_comments == query:
                    changed = False
                break
        if not found:
            return 0
        else:
            if not changed:
                return 1
            else:
                return 2

    def addOrUpdateQuery(self, title, endpoint, query):
        """Update an already existing query
           Create new version"""

        ob = None

        changed = True
        for sparql in self.values():
            if sparql.title == title:
                latest_sparql = versions.get_versions_api(
                    sparql).latest_version()
                ob = latest_sparql
                if latest_sparql.query_with_comments == query:
                    changed = False
                break

        if not ob:
            _id = self.generateUniqueId("Sparql")
            _id = self.invokeFactory(type_name="Sparql", id=_id)
            ob = self[_id]
            ob.edit(
                title          = title,
                endpoint_url   = endpoint,
                sparql_query   = query,
            )
            ob._renameAfterCreation(check_auto_id=True)
        else:
            if changed:
                ob = versions.create_version(ob)
                ob.edit(
                    sparql_query   = query,
                )

        return ob

    def findQuery(self, title):
        """Find the Query in the bookmarks folder
        """

        ob = None
        for sparql in self.values():
            if sparql.title == title:
                latest_sparql = versions.get_versions_api(
                    sparql).latest_version()
                ob = latest_sparql
                break
        return ob

    def syncQueries(self):
        """sync all queries from bookmarks"""
        queries = self.execute()['result']['rows']
        for query in queries:
            query_name = query[0].value
            query_sparql = query[2].value
            self.addOrUpdateQuery(query_name,
                     self.endpoint_url,
                     query_sparql)

atapi.registerType(Sparql, PROJECTNAME)
atapi.registerType(SparqlBookmarksFolder, PROJECTNAME)
