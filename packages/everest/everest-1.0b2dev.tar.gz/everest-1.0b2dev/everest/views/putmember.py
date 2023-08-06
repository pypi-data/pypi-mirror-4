"""
Put member view.

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Oct 14, 2011.
"""
from everest.resources.utils import resource_to_url
from everest.views.base import PutOrPostResourceView
from webob.exc import HTTPOk

__docformat__ = 'reStructuredText en'
__all__ = ['PutMemberView',
           ]


class PutMemberView(PutOrPostResourceView):
    """
    View for PUT requests on member resources.

    The client sends a PUT request to store a representation of a Member
    Resource. If the request is successful, the server responds with a status
    code of 200.

    See http://bitworking.org/projects/atom/rfc5023.html#edit-via-PUT
    """
    def _process_request_data(self, data):
        initial_name = self.context.__name__
        self.context.update_from_data(data)
        current_name = self.context.__name__
        self.request.response.status = self._status(HTTPOk)
        # FIXME: add conflict detection
        if initial_name != current_name:
            self.request.response.headerlist = \
                [('Location',
                  resource_to_url(self.context, request=self.request))]
        # We return the (representation of) the updated member to
        # assist the client in doing the right thing. 
        # Not all clients give access to the Response headers and we 
        # cannot find the new location when HTTP/1.1 301 is returned.
        return self._get_result(self.context)
