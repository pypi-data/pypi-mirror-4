from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from cs.featured import featuredMessageFactory as _

# -*- extra stuff goes here -*-

class Ifeatured(Interface):
    """Description of Featured"""
