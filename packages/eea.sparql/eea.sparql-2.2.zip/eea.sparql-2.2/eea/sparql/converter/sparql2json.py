""" Convert sparql results to json
"""

import sparql
import json as simplejson
from zope.component import queryUtility
from eea.sparql.converter import IGuessType
from Products.ZSPARQLMethod import Method

#define our own converters
sparql_converters = Method.sparql_converters.copy()
sparql_converters[sparql.XSD_DECIMAL] = float
sparql_converters[sparql.XSD_DATE] = str
sparql_converters[sparql.XSD_DATETIME] = str
sparql_converters[sparql.XSD_TIME] = str

propertytype_dict = {
    "": "text",
    sparql.XSD_STRING: "text",
    sparql.XSD_INTEGER: "number",
    sparql.XSD_INT: "number",
    sparql.XSD_LONG: "number",
    sparql.XSD_DOUBLE: "number",
    sparql.XSD_FLOAT: "number",
    sparql.XSD_DECIMAL: "number",
    sparql.XSD_DATETIME: "date",
    sparql.XSD_DATE: "date",
    sparql.XSD_TIME: "date",
    sparql.XSD_BOOLEAN: "boolean",
}

class MethodResult (Method.MethodResult):
    """Override MethodResult with our sparql_converters"""
    def __iter__(self):
        return (sparql.unpack_row(r, convert_type=sparql_converters)
                for r in self.rdfterm_rows)

    def __getitem__(self, n):
        return sparql.unpack_row(self.rdfterm_rows[n],
                                 convert_type=sparql_converters)

def sparql2json(data, column_types=None):
    """
    Converts sparql to JSON

        >>> from eea.sparql.converter import sparql2json
        >>> from eea.sparql.tests import mock_data
        >>> from eea.sparql.converter.sparql2json import sparql2json
        >>> test_data = mock_data.loadSparql()
        >>> data = sparql2json(test_data)
        >>> print (data['items'])
        [{'name': u'NAME',
        'double': 2.5,
        'decimal': 5.21,
        'float': 4.5,
        'long': 15,
        'label': 0,
        'boolean': True,
        'time': '2012-01-10 14:31:27',
        'date': '14:31:03',
        'integer': 1,
        'datetime': '2012-01-10',
        'string': u'STRING'},
        {'name': u'',
        'double': 0.0,
        'decimal': 0.0,
        'float': 0.0,
        'long': 0,
        'label': 1,
        'boolean': False,
        'time': '',
        'date': '',
        'integer': 0,
        'datetime': '',
        'string': u''}]

    """
    data_result = data['result']
    items = []
    hasLabel = False
    mr = MethodResult(data)

    cols = mr.var_names
    properties = {}

    for index, col in enumerate(cols):
        if col.lower().endswith(":label") or col.lower()=="label":
            cols[index] = 'label'
            hasLabel = True
            break

    for index, row in enumerate(mr):
        rowdata = {}
        if not hasLabel:
            rowdata['label'] = index

        for idx, item in enumerate(row):
            key = cols[idx].encode('utf8')
            valueType = 'text'
            if isinstance(data_result['rows'][0][idx], sparql.Literal):
                datatype = data_result['rows'][0][idx].datatype
                if not datatype:
                    datatype = ''
                valueType = propertytype_dict[datatype]
            elif isinstance(data_result['rows'][0][idx], sparql.IRI):
                valueType = 'url'

            rowdata[key] = item

            # Enforce column_types
            columnType = valueType
            if column_types:
                newColumnType = column_types.get(key, columnType)
                if newColumnType == columnType:
                    continue

                columnType = newColumnType
                guess = queryUtility(IGuessType, name=columnType)
                valueType = getattr(guess, 'valueType', valueType)
                fmt = getattr(guess, 'fmt', None)
                try:
                    item = u'%s' % item
                    item = (guess.convert(item, fallback=None, format=fmt)
                            if guess else item)
                except Exception:
                    rowdata.pop(key)
                else:
                    rowdata[key] = item

            properties[key] = {
                'columnType': columnType,
                "valueType" : valueType,
                "order" : idx
            }

        items.append(rowdata)

    return {'items': items, 'properties': properties}

def sortProperties(strJson, indent = 0):
    """
    In the json string set the correct order of the columns
    """
    try:
        json = simplejson.loads(strJson)
        properties = json['properties']
        indentStr1 = ""
        indentStr2 = ""
        indentStr3 = ""
        if indent > 0:
            indentStr1 = "\n" + " " * indent
            indentStr2 = "\n" + " " * indent * 2
            indentStr3 = "\n" + " " * indent * 3
        newProperties = []
        for key, item in properties.items():
            prop = []
            prop.append(item['order'])
            prop.append(key)
            prop.append(item['valueType'])
            newProperties.append(prop)
        newProperties.sort()
        json['properties'] = ''
        newJsonStr = simplejson.dumps(json, indent = indent)
        newPropStr = '"properties": '
        newPropStr += "{"
        for prop in newProperties:
            newPropStr += indentStr2 + '"' + prop[1] + '": '
            newPropStr += '{'
            newPropStr += indentStr3 + '"valueType": "' + prop[2] +'", '
            newPropStr += indentStr3 + '"order": ' + str(prop[0]) + indentStr2
            newPropStr += '}, '
        if newProperties:
            newPropStr = newPropStr[:-2]
        newPropStr += indentStr1 + "}"
        newJsonStr = newJsonStr.replace('"properties": ""', newPropStr)
        return newJsonStr
    except Exception:
        return strJson
