"""
Post collection view.

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Oct 14, 2011.
"""
from everest.resources.attributes import ResourceAttributeKinds
from everest.resources.utils import get_member_class
from everest.resources.utils import provides_member_resource
from everest.resources.utils import provides_resource
from everest.resources.utils import resource_to_url
from everest.views.base import PutOrPostResourceView
from webob.exc import HTTPCreated

__docformat__ = 'reStructuredText en'
__all__ = ['PostCollectionView',
           ]


class PostCollectionView(PutOrPostResourceView):
    """
    View for POST requests on collection resources.

    The client POSTs a representation of the member to the URI of the
    collection. If the new member resource was created successfully, the 
    server responds with a status code of 201 and a Location header that 
    contains the IRI of the newly created resource and a representation 
    of it in the body of the response.

    See http://bitworking.org/projects/atom/rfc5023.html#post-to-create
    """
    def _process_request_data(self, data):
        if not provides_resource(data):
            rpr = self._get_request_representer()
            resource = rpr.resource_from_data(data)
        else:
            resource = data
        member_was_posted = provides_member_resource(resource)
        if member_was_posted:
            new_members = [resource]
        else:
            new_members = resource
        was_created = True
        parent_collection_is_nested = self.context.is_nested
        for new_member in new_members:
            if parent_collection_is_nested:
                # If we are POSTing to a nested collection, the framework
                # tries to infer the parent for each member if it has not
                # been provided by the representation.
                self.__check_parent(new_member)
            if self.context.get(new_member.__name__) is not None:
                # We have a member with the same name - 409 Conflict.
                response = self._handle_conflict(new_member.__name__)
                was_created = False
                break
            else:
                self.context.add(new_member)
        if was_created:
            if member_was_posted:
                new_location = resource_to_url(resource, request=self.request)
            else:
                new_location = resource_to_url(self.context,
                                               request=self.request)
            self.request.response.status = self._status(HTTPCreated)
            self.request.response.headerlist = [('Location', new_location)]
            response = self._get_result(resource)
        return response

    def __check_parent(self, new_mb_rc):
        parent_mb_cls = get_member_class(self.context.__parent__)
        for attr_name, attr in type(new_mb_rc).get_attributes().iteritems():
            if attr.kind == ResourceAttributeKinds.MEMBER \
               and get_member_class(attr.value_type) is parent_mb_cls \
               and getattr(new_mb_rc, attr_name) is None:
                setattr(new_mb_rc, attr_name, self.context.__parent__)
