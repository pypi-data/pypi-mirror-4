"""Definition of the Sparql content type
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata, base
from Products.ATContentTypes.content.folder import ATFolder

from Products.Archetypes import atapi
from Products.Archetypes.atapi import IntegerField
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField, StringWidget, \
                                        BooleanWidget, BooleanField
from Products.Archetypes.atapi import TextField, TextAreaWidget
from Products.ZSPARQLMethod.Method import ZSPARQLMethod, \
                                        interpolate_query, \
                                        run_with_timeout, \
                                        parse_arg_spec, \
                                        query_and_get_result, \
                                        map_arg_values
from AccessControl.Permissions import view
from eea.sparql.cache import ramcache, cacheSparqlKey
from eea.sparql.config import PROJECTNAME
from eea.sparql.interfaces import ISparql, ISparqlBookmarksFolder
from eea.versions.interfaces import IVersionEnhanced
from eea.versions import versions

from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError

from AccessControl import SpecialUsers
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, \
                                            setSecurityManager

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
            macro="sparql_textfield_with_preview",
            helper_js=("sparql_textfield_with_preview.js",),
            helper_css=("sparql_textfield_with_preview.css",),
            label="Query",
        ),
        required=1
    ),
    BooleanField(
        name='sparql_static',
        widget=BooleanWidget(
            label='Static query',
            description='The data will be fetched only once',
        ),
        default=False,
        required=0
    ),
    TextField(
        name='sparql_results',
        widget=TextAreaWidget(
            label="Results",
            visible={'edit': 'invisible', 'view': 'invisible' }
        ),
        required=0,

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
SparqlBookmarksFolderSchema['sparql_static'].widget.visible['edit'] = \
        'invisible'

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

    security.declareProtected(view, 'invalidateWorkingResult')
    def invalidateWorkingResult(self):
        """ invalidate working results"""
        self.cached_result = {}
        self.setSparql_results("")
        pr = getToolByName(self, 'portal_repository')
        comment = "Invalidated last working result"
        comment = comment.encode('utf')
        try:
            pr.save(obj=self, comment=comment)
        except FileTooLargeToVersionError:
            commands = view.getCommandSet('plone')
            commands.issuePortalMessage(
                """Changes Saved. Versioning for this file 
                   has been disabled because it is too large.""",
                msgtype="warn")

    security.declareProtected(view, 'execute')
    def execute(self, **arg_values):
        """
        Override execute from ZSPARQLMethod in order to have a default timeout
        """
        cached_result = getattr(self, 'cached_result', {})
        cooked_query = interpolate_query(self.query, arg_values)

        force_requery = False

        if not self.getSparql_static():
            force_requery = True

        if cached_result == {}:
            force_requery = True

        if force_requery:
            args = (self.endpoint_url, cooked_query)
            new_result = run_with_timeout(
                max(getattr(self, 'timeout', 10), 10),
                query_and_get_result,
                *args)

            force_save = False

            if new_result.get("result", {}) != {}:
                if new_result != cached_result:
                    if len(new_result.get("result", {}).get("rows", {})) > 0:
                        force_save = True
                    else:
                        if len(cached_result.get('result', {}).\
                            get('rows', {})) == 0:
                            force_save = True

            if force_save:
                self.cached_result = new_result
                new_sparql_results = u""
                for row in self.cached_result.get('result', {}).get('rows', {}):
                    for val in row:
                        new_sparql_results = new_sparql_results + \
                            unicode(val) + " | "
                    new_sparql_results = new_sparql_results[0:-3] + "\n"
                    self.setSparql_results(new_sparql_results)
                pr = getToolByName(self, 'portal_repository')
                if self.portal_type in pr.getVersionableContentTypes():
                    comment = "Result changed"
                    comment = comment.encode('utf')

                    oldSecurityManager = getSecurityManager()
                    newSecurityManager(self.REQUEST, SpecialUsers.system)
                    try:
                        pr.save(obj=self, comment=comment)
                    except FileTooLargeToVersionError:
                        commands = view.getCommandSet('plone')
                        commands.issuePortalMessage(
                            """Changes Saved. Versioning for this file 
                               has been disabled because it is too large.""",
                            msgtype="warn")
                    setSecurityManager(oldSecurityManager)

            if new_result.get('exception', None):
                self.cached_result['exception'] = new_result['exception']
        return self.cached_result

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
