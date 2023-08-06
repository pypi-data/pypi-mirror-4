"""
Parent/child relationship between entities or resources.

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Sep 30, 2011.
"""
from everest.querying.utils import get_filter_specification_factory

__docformat__ = 'reStructuredText en'
__all__ = ['Relationship',
           ]


class Relationship(object):
    """
    Represents a nested relationship between a parent object and a collection 
    of child objects.
    
    This is used for deferred access of child objects and for dynamic creation
    of a filter specification for the children.

    :ivar parent: parent object
    :ivar children: child object collection
    :ivar backref: name of the attribute referencing the parent in
        each child object.
    """
    def __init__(self, parent, children=None, backref=None):
        if children is None and backref is None:
            raise ValueError('Do not know how to create a relationship '
                             'if neither a children container nor a back '
                             'referencing attribute are given.')
        self.parent = parent
        self.children = children
        self.backref = backref

    @property
    def specification(self):
        spec_fac = get_filter_specification_factory()
        if not self.backref is None:
            # Simple case: We have an attribute in the child that references
            # the parent and we can identify all elements of the child
            # collection with an "equal_to" specification.
            rel_spec = spec_fac.create_equal_to(self.backref,
                                                self.parent)
        else:
            # Complex case: We use the IDs of the elements of the child
            # collection to form a "contained" specification. This is slow
            # because we need to iterate over the whole collection.
            elems = self.children
            if len(elems) > 0:
                ids = [elem.id for elem in elems]
                rel_spec = spec_fac.create_contained('id', ids)
            else:
                # Create impossible search criterion for empty collection.
                rel_spec = spec_fac.create_equal_to('id', None)
        return rel_spec
