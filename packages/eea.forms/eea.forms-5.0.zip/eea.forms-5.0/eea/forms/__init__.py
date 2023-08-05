""" Widgets
"""
from eea.forms import validators
validators.register()

from eea.forms import fields
fields.register()

from eea.forms import widgets
widgets.register()

def initialize(context):
    """ Zope 2 initialize
    """
    return
