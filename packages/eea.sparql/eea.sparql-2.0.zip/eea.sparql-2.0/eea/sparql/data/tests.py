""" Doc tests
"""
import logging
import doctest
import unittest
from eea.sparql.tests.base import FUNCTIONAL_TESTING
from plone.testing import layered
logger = logging.getLogger('eea.sparql')

VISUALIZATION = None
try:
    from eea.app.visualization import interfaces as VISUALIZATION
except ImportError, err:
    logger.debug(err)

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()
    if VISUALIZATION:
        suite.addTests([
            layered(
                doctest.DocFileSuite(
                    'data/source.py',
                    optionflags=OPTIONFLAGS,
                    package='eea.sparql'),
                layer=FUNCTIONAL_TESTING),
        ])
    return suite
