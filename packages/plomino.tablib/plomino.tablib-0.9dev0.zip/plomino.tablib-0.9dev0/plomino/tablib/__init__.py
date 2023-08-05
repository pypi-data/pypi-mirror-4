from zope import component
from Products.CMFPlomino import interfaces
from zope.interface import implements

# TODO: support more of these:
# from tablib import Databook, Dataset, detect, import_set, InvalidDatasetType, InvalidDimensions, UnsupportedFormat

from tablib import Dataset
from tablib import Databook

from Products.PythonScripts.Utility import allow_module, allow_class

allow_module('plomino.tablib')
allow_class(Dataset)
allow_class(Databook)

def dataset(data, headers=None):
    """ `data` is a list of dicts.
    """
    dataset = Dataset()
    dataset.dict = data
    if headers:
        dataset.headers = headers
    return dataset

def databook(data):
    """ `data` is a tuple of datasets.
    """
    return Databook(data)

class PlominoTablibUtils:
    implements(interfaces.IPlominoUtils)

    module = 'plomino.tablib'
    methods = ['dataset', 'databook']

component.provideUtility(PlominoTablibUtils, interfaces.IPlominoUtils, name='plomino.tablib')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

