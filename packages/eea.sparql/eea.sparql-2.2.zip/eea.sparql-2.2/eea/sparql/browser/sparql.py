""" sparql
"""
import logging
import csv
from Products.Five import BrowserView
from Products.ZSPARQLMethod.Method import interpolate_query_html
from Products.ZSPARQLMethod.Method import map_arg_values
from Products.ZSPARQLMethod.Method import parse_arg_spec
from eea.sparql.converter.sparql2json import sparql2json
from eea.sparql.converter.sparql2json import sortProperties
from eea.versions import versions
from Products.CMFCore.utils import getToolByName
from time import time
import json
import urllib2
import contextlib

logger = logging.getLogger('eea.sparql')

class ExcelTSV(csv.excel):
    """ CSV Tab Separated Dialect
    """
    delimiter = '\t'
csv.register_dialect("excel.tsv", ExcelTSV)

class Sparql(BrowserView):
    """Sparql view"""

    def test_query(self):
        """test query"""
        arg_spec = parse_arg_spec(self.context.arg_spec)
        missing, arg_values = map_arg_values(arg_spec, self.request.form)
        error = None

        if missing:
            # missing argument
            data = None
            dt = 0

        else:
            t0 = time()

            res, error = {}, None
            try:
                res = self.context.execute(**arg_values)
            except Exception:
                import traceback
                error = traceback.format_exc()
            data = res.get('result')
            error = error or res.get('exception')

            dt = time() - t0

        options = {
            'query': interpolate_query_html(self.context.query, arg_values),
            'query_with_comments': interpolate_query_html(
                self.context.query_with_comments, arg_values),
            'data': data,
            'duration': dt,
            'arg_spec': arg_spec,
            'error': error,
        }
        return options

    def json(self, column_types=None):
        """json"""
        data = self.context.execute_query()
        return sortProperties(json.dumps(sparql2json(data, column_types)))

    def sparql2exhibit(self):
        """ Download sparql results as Exhibit JSON
        """
        try:
            data = sparql2json(self.context.execute_query())
        except Exception:
            data = {'properties':{}, 'items':{}}

        self.request.response.setHeader(
            'Content-Type', 'application/json')
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s.exhibit.json"' % self.context.getId())
        return sortProperties(json.dumps(data))

    def sparql2html(self):
        """ Download sparql results as HTML
        """
        try:
            data = sparql2json(self.context.execute_query())
        except Exception:
            data = {'properties':{}, 'items':{}}

        result = []
        result.append(u"<style type='text/css'>")
        result.append(u"table {border-collapse: collapse }")
        result.append( u"th, td {border:1px solid black}")
        result.append(u"</style>")
        result.append(u"<table>")
        result.append(u"\t<tr>")

        properties = []
        def_order = 0
        for key, item in data['properties'].items():
            prop = []
            prop.append(item.get('order', def_order))
            prop.append(key)
            prop.append(item['valueType'])
            properties.append(prop)
            def_order += 1
        properties.sort()

        for col in properties:
            result.append(u"\t\t<th>" + col[1] + u"</th>")
        result.append(u"\t</tr>")
        for row in data['items']:
            result.append(u"\t<tr>")
            for col in properties:
                result.append(u"\t\t<td>" + unicode(row[col[1]]) + "</td>")
            result.append(u"\t</tr>")
        result.append(u"</table>")
        return '\n'.join(result)

    def sparql2csv(self, dialect='excel'):
        """ Download sparql results as Comma Separated File
        """
        try:
            data = sparql2json(self.context.execute_query())
        except Exception:
            data = {'properties':{}, 'items':{}}

        if dialect == 'excel':
            self.request.response.setHeader(
                'Content-Type', 'application/csv')
            self.request.response.setHeader(
                'Content-Disposition',
                'attachment; filename="%s.csv"' % self.context.getId())
        else:
            self.request.response.setHeader(
                'Content-Type', 'application/tsv')
            self.request.response.setHeader(
                'Content-Disposition',
                'attachment; filename="%s.tsv"' % self.context.getId())

        writter = csv.writer(self.request.response, dialect=dialect)
        row = []

        properties = []
        def_order = 0
        for key, item in data['properties'].items():
            prop = []
            prop.append(item.get('order', def_order))
            prop.append(key)
            prop.append(item['valueType'])
            properties.append(prop)
            def_order += 1
        properties.sort()

        headers = []
        for prop in properties:
            headers.append(prop[1])

        for col in headers:
            header = '%s:%s' % (col, data['properties'][col]['valueType'])
            row.append(header)
        writter.writerow(row)

        for item in data['items']:
            row = []
            for col in headers:
                row.append(unicode(item[col]))
            writter.writerow(row)

        return ''

    def sparql2tsv(self, dialect='excel.tsv'):
        """ Download sparql results as Tab Separated File
        """
        return self.sparql2csv(dialect=dialect)

    def sparql2json(self):
        """ Download sparql results as JSON
        """
        headers = {'Accept' : 'application/sparql-results+json'}
        self.request.response.setHeader(
            'Content-Type', 'application/json')
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s.json"' % self.context.getId())
        return self.sparql2response(headers=headers)

    def sparql2xml(self):
        """ Download sparql results as XML
        """
        headers = {'Accept' : 'application/sparql-results+xml'}
        self.request.response.setHeader(
            'Content-Type', 'application/xml')
        self.request.response.setHeader(
            'Content-Disposition',
                'attachment; filename="%s.xml"' % self.context.getId())
        return self.sparql2response(headers=headers)

    def sparql2xmlWithSchema(self):
        """ Download sparql results as XML with schema
        """
        headers = {'Accept' : 'application/x-ms-access-export+xml'}
        self.request.response.setHeader(
            'Content-Type', 'application/xml')
        self.request.response.setHeader(
            'Content-Disposition',
                'attachment; filename="%s.schema.xml"' % self.context.getId())
        return self.sparql2response(headers=headers)

    def sparql2response(self, headers=None):
        """ Write
        """
        endpoint = self.context.endpoint_url
        query = 'query=%s' % self.context.query
        request = urllib2.Request(endpoint, query, headers or {})
        results = ""
        timeout = max(getattr(self.context, 'timeout', 10), 10)
        try:
            with contextlib.closing(urllib2.urlopen(
                request, timeout = timeout)) as conn:
                for data in conn:
                    self.request.response.write(data)
        except Exception, err:
            logger.exception(err)
        return results

    def isDavizInstalled(self):
        """ Check if Daviz is installed
        """
        has_daviz = False
        try:
            from eea.daviz import interfaces
            has_daviz = bool(interfaces)

        except ImportError:
            has_daviz = False

        return has_daviz


class SparqlBookmarksFolder(Sparql):
    """SparqlBookmarksFolder view"""

    def getBookmarks(self):
        """Get list of bookmarks and check if needs to be updated"""
        results = self.test_query()
        queries = results['data'].get('rows', [])
        bookmarks = {}
        bookmarks['data'] = []
        bookmarks['arg_spec'] = results['arg_spec']
        bookmarks['error'] = results['error']
        bookmarks['duration'] = results['duration']
        query_endpoint = self.context.endpoint_url
        for query in queries:
            query_details = {}
            query_details['name'] = query[0].value
            query_details['sparql'] = query[2].value
            query_details['bookmark'] = query[1].value
            query_details['status'] = self.context.checkQuery(
                                        query_details['name'],
                                        query_endpoint,
                                        query_details['sparql'])
            bookmarks['data'].append(query_details)
        return bookmarks

    def addOrUpdateQuery(self):
        """Add or Update the Current Query"""
        ob = self.context.addOrUpdateQuery(self.request['title'],
                 self.context.endpoint_url,
                 self.request['query'])
        self.request.response.redirect(ob.absolute_url() + "/@@view")

    def syncQueries(self):
        """Synchronize all Queries"""
        self.context.syncQueries()
        self.request.response.redirect(self.context.absolute_url() + "/@@view")

    def getVisualizations(self, title):
        """ Get Daviz Visualizations for sparql object
        """
        ob = None
        for sparql in self.context.values():
            if sparql.title == title:
                ob = versions.get_versions_api(
                    sparql).latest_version()
                break
        if not ob:
            return []

        return ob.getBRefs('relatesTo')

    def createVisualization(self):
        """ Create visualization with datasource
        """
        ob = self.context.findQuery(self.request['title'])
        if ob:
            self.request.response.redirect(ob.absolute_url() +
                "/daviz-create-new.html")

class SparqlBookmarkFoldersSync(BrowserView):
    """ Sync all Bookmark Folders """

    def __call__(self):
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog.searchResults(portal_type = 'SparqlBookmarksFolder')
        for brain in brains:
            try:
                brain.getObject().syncQueries()
            except Exception, err:
                logger.exception(err)
        return "Sync done"
