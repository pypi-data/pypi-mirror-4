"""
Interfaces for everest.

This file is part of the everest project.
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Oct 14, 2011.
"""
from zope.interface import Interface # pylint: disable=E0611,F0401
from zope.schema import Bool # pylint: disable=E0611,F0401
from zope.schema import List # pylint: disable=E0611,F0401
from zope.schema import Text # pylint: disable=E0611,F0401

__docformat__ = 'reStructuredText en'
__all__ = ['IAtomMime',
           'IAtomEntryMime',
           'IAtomFeedMime',
           'IAtomRequest',
           'IAtomServiceMime',
           'ICsvMime',
           'ICsvRequest',
           'IHtmlRequest',
           'IHtmlMime',
           'IJsonMime',
           'IJsonRequest',
           'IUserMessage',
           'IUserMessageChecker',
           'IUserMessageNotifier',
           'IXmlMime',
           'IXmlRequest',
           'IXlsMime',
           'IXlsRequest',
           'IZipMime'
           ]

# no self, no __init__, no args  pylint: disable=E0213,W0232,E0211

class IJsonRequest(Interface):
    """Marker interface for a JSON request."""


class IAtomRequest(Interface):
    """Marker interface for an ATOM request."""


class IXmlRequest(Interface):
    """Marker interface for an XML request."""


class ICsvRequest(Interface):
    """Marker interface for an request."""


class IHtmlRequest(Interface):
    """Marker interface for a HTML request."""


class IXlsRequest(Interface):
    """Marker interface for an Excel request."""


class IZipRequest(Interface):
    """Marker interface for an Zip compressed request."""


class IMime(Interface):
    """Base Interface for all MIME content types."""
    mime_type_string = Text(title=u'MIME string for this MIME content type. '
                                   '(e.g., "application/json".')
    representer_name = Text(title=u'Name of the representer associated with '
                                   'this MIME content type (e.g., "json").')
    file_extensions = List(title=u'Known file extensions for this MIME '
                                  'content type.')

class IJsonMime(IMime):
    """Interface for JSON mime type."""


class IAtomMime(IMime):
    """Interface for ATOM mime type."""


class IXmlMime(IMime):
    """Interface for XML mime type."""


class ICsvMime(IMime):
    """Interface for CSV mime type."""


class IXlsMime(IMime):
    """Interface for Excel mime type."""


class IZipMime(IMime):
    """Interface for Zip compressed mime type."""


class IHtmlMime(IMime):
    """Interface for HTML mime type."""


class ITextPlainMime(IMime):
    """Interface for Plain Text mime type."""


class IAtomFeedMime(Interface):
    """Marker interface for ATOM feed mime type."""


class IAtomEntryMime(Interface):
    """Marker interface for ATOM entry mime type."""


class IAtomServiceMime(Interface):
    """Marker interface for ATOM service mime type."""


class IUserMessage(Interface):
    text = Text(title=u'message text.')


class IUserMessageNotifier(Interface):
    def notify(message_text):
        """
        Notifies all subscribers to 
        :class:`everest.messaging.IUserMessage` of the given message
        and returns their collective vote.
        
        :param str message_text: message to notify subcribers about. The
          notifier will need to convert this to a :class:`UserMessage` 
          instance.
        """


class IUserMessageChecker(Interface):
    def __call__(message):
        """
        This is required so that instances of user message checkers can
        serve as an adapter to a user message.
        
        :param message: message to check
        :type message: :class:`everest.entities.system.UserMessage`.
        """

    def check():
        """
        Evaluates the message held by this checker. Returns `False`, 
        `True`, or `None` to signal abortion, continuation conditional on 
        other checkers approval, or unconditional continuation to the caller. 
        """

    vote = Bool(title=u'Result of the voting from all subscribed checkers.')


class IResourceUrlConverter(Interface):
    def url_to_resource(url):
        """Performs URL -> resource conversion."""
    def resource_to_url(resource):
        """Performs URL -> resource conversion."""

# pylint: enable=E0213,W0232,E0211
