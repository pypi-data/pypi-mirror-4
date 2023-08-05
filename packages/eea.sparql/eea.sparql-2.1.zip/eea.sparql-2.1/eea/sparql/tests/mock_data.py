""" Mock data for testing
"""

from eea.sparql.content.sparql import Sparql
from Products.ZSPARQLMethod.Method import parse_arg_spec, map_arg_values
from eea.sparql.tests.base import PORT

def mock_sparql_query():
    """ mock query for sparql """
    return "mock"

def loadSparql():
    """ Load data from mock http
    """
    sparql = Sparql(0)
    sparql.endpoint_url = "http://localhost:"+str(PORT)+"/sparql-results.xml"
    sparql.sparql_query = mock_sparql_query
    sparql.timeout = None
    sparql.arg_spec = ""

    args = None
    arg_spec = parse_arg_spec(sparql.arg_spec)
    arg_values = map_arg_values(arg_spec, args)[1]
    data = sparql.execute(**sparql.map_arguments(**arg_values))

    return data